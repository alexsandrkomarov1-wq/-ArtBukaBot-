"""KOMAROVA_CORE file registry engine.

The engine stores verified copies of imported files and records their metadata
in an existing SQLite materials table. It never modifies source files.

Configuration (all optional):
    KOMAROVA_CORE_ROOT  project root (default: ~/Desktop/KOMAROVA_CORE)
    KOMAROVA_DB_FILE    SQLite database path (overrides CORE_ROOT default)
    KOMAROVA_STORAGE    verified-file storage directory
    KOMAROVA_LOG_DIR    import/export log directory
"""
from __future__ import annotations

import hashlib
import mimetypes
import os
import shutil
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(os.environ.get("KOMAROVA_CORE_ROOT", Path.home() / "Desktop" / "KOMAROVA_CORE")).expanduser()
DB_FILE = Path(os.environ.get("KOMAROVA_DB_FILE", ROOT / "core" / "data_registry" / "komarova.db")).expanduser()
STORAGE = Path(os.environ.get("KOMAROVA_STORAGE", ROOT / "storage" / "verified")).expanduser()
LOG_DIR = Path(os.environ.get("KOMAROVA_LOG_DIR", ROOT / "storage" / "import_logs")).expanduser()

FORMATS = {
    ".jpg": "PHOTO", ".jpeg": "PHOTO", ".png": "PHOTO", ".heic": "PHOTO",
    ".tif": "PHOTO", ".tiff": "PHOTO", ".mp4": "VIDEO", ".mov": "VIDEO",
    ".avi": "VIDEO", ".mkv": "VIDEO", ".pdf": "DOCUMENT", ".doc": "DOCUMENT",
    ".docx": "DOCUMENT", ".txt": "DOCUMENT", ".xls": "SPREADSHEET",
    ".xlsx": "SPREADSHEET", ".csv": "SPREADSHEET", ".ppt": "PRESENTATION",
    ".pptx": "PRESENTATION", ".zip": "ARCHIVE",
}
REQUIRED_COLUMNS = {
    "material_id", "file_name", "sha256", "received_time", "file_type",
    "extension", "original_path", "stored_path", "file_size", "mime_type",
    "file_status", "geo_status",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    if not DB_FILE.is_file():
        raise FileNotFoundError(f"База KOMAROVA_CORE не найдена: {DB_FILE}")
    db = sqlite3.connect(DB_FILE, timeout=30)
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("PRAGMA busy_timeout = 30000")
    return db


def _columns(db: sqlite3.Connection) -> set[str]:
    table = db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='materials'"
    ).fetchone()
    if not table:
        raise RuntimeError("В базе отсутствует таблица materials; автоматическое создание запрещено.")
    return {row[1] for row in db.execute("PRAGMA table_info(materials)")}


def prepare() -> None:
    # Validate the existing schema before creating any directories or indexes.
    with connect() as db:
        missing = REQUIRED_COLUMNS - _columns(db)
        if missing:
            raise RuntimeError("В materials отсутствуют обязательные поля: " + ", ".join(sorted(missing)))
        db.execute("CREATE INDEX IF NOT EXISTS idx_materials_sha256 ON materials(sha256)")
    STORAGE.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def calculate_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def log(message: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with (LOG_DIR / "file_engine.log").open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(f"{now()} | {message}\n")


def _material_rows(db: sqlite3.Connection, digest: str) -> list[tuple[str, str | None]]:
    return db.execute(
        "SELECT material_id, stored_path FROM materials WHERE sha256=? ORDER BY received_time, material_id",
        (digest,),
    ).fetchall()


def _verified_duplicate(rows: Iterable[tuple[str, str | None]], digest: str) -> tuple[str, str] | None:
    for material_id, stored_path in rows:
        if stored_path:
            path = Path(stored_path)
            if path.is_file() and calculate_hash(path) == digest:
                return material_id, str(path)
    return None


def import_file(source: str | Path) -> str | None:
    source = Path(source).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Файл не найден: {source}")
    extension = source.suffix.lower()
    if extension not in FORMATS:
        raise ValueError(f"Формат не поддерживается: {extension or '(без расширения)'}")

    prepare()
    digest = calculate_hash(source)
    size = source.stat().st_size
    category = FORMATS[extension]
    mime = mimetypes.guess_type(source.name)[0] or "application/octet-stream"

    db = connect()
    temp_path: Path | None = None
    final_path: Path | None = None
    created_final = False
    committed = False
    material_id: str | None = None
    try:
        db.execute("BEGIN IMMEDIATE")
        rows = _material_rows(db, digest)
        duplicate = _verified_duplicate(rows, digest)
        if duplicate:
            db.commit()
            material_id = duplicate[0]
            print(f"Дубликат уже зарегистрирован. MATERIAL-ID: {material_id}")
            return material_id

        # Reuse the earliest registry ID if its archived bytes are missing.
        repair_row = next(((mid, stored) for mid, stored in rows), None)
        recovered_existing = False
        if repair_row:
            material_id, old_path = repair_row
            if old_path:
                previous_path = Path(old_path)
                if previous_path.exists():
                    # Never overwrite a damaged archive object. Keep it as evidence
                    # and write the verified replacement to a new immutable path.
                    recovered_existing = True
                    final_path = (
                        STORAGE / category.lower()
                        / f"{material_id}.recovered-{uuid.uuid4().hex[:8]}{extension}"
                    )
                else:
                    # A missing object can safely be restored at its registered path.
                    final_path = previous_path
            else:
                final_path = STORAGE / category.lower() / f"{material_id}{extension}"
        else:
            material_id = f"KOM-{category}-{uuid.uuid4().hex[:12].upper()}"
            final_path = STORAGE / category.lower() / f"{material_id}{extension}"

        final_path.parent.mkdir(parents=True, exist_ok=True)
        if final_path.exists():
            raise FileExistsError(f"Путь назначения уже занят, перезапись запрещена: {final_path}")

        temp_path = final_path.with_name(final_path.name + f".{uuid.uuid4().hex}.part")
        shutil.copy2(source, temp_path)
        copied_hash = calculate_hash(temp_path)
        if copied_hash != digest:
            raise RuntimeError("SHA-256 копии не совпадает с источником.")
        if source.stat().st_size != size:
            raise RuntimeError("Исходный файл изменился во время импорта.")

        os.replace(temp_path, final_path)
        temp_path = None
        created_final = True

        if repair_row:
            db.execute(
                """UPDATE materials SET file_name=?, sha256=?, received_time=?, file_type=?,
                   extension=?, original_path=?, stored_path=?, file_size=?, mime_type=?,
                   file_status='verified' WHERE material_id=?""",
                (source.name, digest, now(), category, extension, str(source), str(final_path),
                 size, mime, material_id),
            )
        else:
            db.execute(
                """INSERT INTO materials (material_id, file_name, sha256, received_time,
                   geo_status, file_type, extension, original_path, stored_path, file_size,
                   mime_type, file_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (material_id, source.name, digest, now(), "not_checked", category, extension,
                 str(source), str(final_path), size, mime, "verified"),
            )
        db.commit()
        committed = True
    except Exception:
        if not committed:
            db.rollback()
            if temp_path and temp_path.exists():
                temp_path.unlink()
            if created_final and final_path and final_path.exists():
                final_path.unlink()
        raise
    finally:
        db.close()

    # The registry transaction is already committed. A log outage must never
    # trigger deletion of a file that the database now references.
    try:
        event = "RECOVERY" if recovered_existing else "IMPORT"
        log(f"{event} | {material_id} | {source.name} | SHA256={digest}")
    except OSError as error:
        print(f"ПРЕДУПРЕЖДЕНИЕ: импорт завершён, но журнал не обновлён: {error}", file=sys.stderr)

    print("ФАЙЛ ЗАРЕГИСТРИРОВАН")
    print("MATERIAL-ID:", material_id)
    print("Реестр: materials")
    print("Категория:", category)
    print("Размер:", size, "байт")
    print("SHA-256:", digest)
    print("Архивная копия:", final_path)
    print("Исходный файл сохранён:", source)
    return material_id


def show_files() -> list[tuple]:
    prepare()
    with connect() as db:
        rows = db.execute(
            """SELECT material_id, file_name, file_type, file_size, file_status
               FROM materials WHERE stored_path IS NOT NULL ORDER BY received_time DESC"""
        ).fetchall()
    print("\nKOMAROVA_CORE: ЕДИНЫЙ РЕЕСТР ФАЙЛОВ")
    print("Всего записей:", len(rows))
    for row in rows:
        print(f"\nID: {row[0]}\nФайл: {row[1]}\nТип: {row[2]}\nРазмер: {row[3]} байт\nСтатус: {row[4]}")
    return rows


def _get_material(material_id: str) -> tuple | None:
    with connect() as db:
        return db.execute(
            "SELECT stored_path, file_name FROM materials WHERE material_id=?", (material_id,)
        ).fetchone()


def open_file(material_id: str) -> None:
    row = _get_material(material_id)
    if not row or not row[0]:
        raise FileNotFoundError("Материал или путь не найден в реестре.")
    path = Path(row[0])
    if not path.is_file():
        raise FileNotFoundError(f"Файл отсутствует в хранилище: {path}")
    if not hasattr(os, "startfile"):
        raise OSError("Команда open поддерживается только в Windows.")
    os.startfile(str(path))


def export_file(material_id: str, target: str | Path) -> Path:
    row = _get_material(material_id)
    if not row or not row[0]:
        raise FileNotFoundError("Материал или путь не найден в реестре.")
    source = Path(row[0])
    target = Path(target).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Архивная копия отсутствует: {source}")
    if target.exists() and target.is_dir():
        target = target / row[1]
    if target.exists():
        raise FileExistsError(f"Файл назначения уже существует, перезапись запрещена: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + f".{uuid.uuid4().hex}.part")
    try:
        shutil.copy2(source, temp)
        if calculate_hash(source) != calculate_hash(temp):
            raise RuntimeError("Проверка SHA-256 экспорта не пройдена.")
        os.replace(temp, target)
    finally:
        if temp.exists():
            temp.unlink()
    try:
        log(f"EXPORT | {material_id} | {target}")
    except OSError as error:
        print(f"ПРЕДУПРЕЖДЕНИЕ: экспорт завершён, но журнал не обновлён: {error}", file=sys.stderr)
    print("Экспорт завершён:", target)
    print("SHA-256 проверен.")
    return target


def verify_files() -> tuple[int, int]:
    prepare()
    with connect() as db:
        rows = db.execute(
            "SELECT material_id, stored_path, sha256, file_size FROM materials WHERE stored_path IS NOT NULL"
        ).fetchall()
    good = errors = 0
    print("\nKOMAROVA_CORE: ПРОВЕРКА ЦЕЛОСТНОСТИ")
    for material_id, stored_path, expected_hash, expected_size in rows:
        path = Path(stored_path)
        if not path.is_file():
            print("ОТСУТСТВУЕТ:", material_id)
            errors += 1
            continue
        actual_size = path.stat().st_size
        actual_hash = calculate_hash(path)
        if actual_hash == expected_hash and actual_size == expected_size:
            print("OK:", material_id)
            good += 1
        else:
            print("ОШИБКА SHA-256/РАЗМЕРА:", material_id)
            errors += 1
    print("\nПроверено:", len(rows), "Совпадений:", good, "Ошибок:", errors)
    return good, errors


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("Команды: init | add <путь> | list | open <MATERIAL-ID> | export <MATERIAL-ID> <путь> | verify")
        return 2
    command = args[0].lower()
    try:
        if command == "init" and len(args) == 1:
            prepare()
            print("KOMAROVA FILE ENGINE: готов.")
            print("Реестр: materials")
            print("Хранилище:", STORAGE)
        elif command == "add" and len(args) >= 2:
            import_file(" ".join(args[1:]))
        elif command == "list" and len(args) == 1:
            show_files()
        elif command == "open" and len(args) == 2:
            open_file(args[1])
        elif command == "export" and len(args) >= 3:
            export_file(args[1], " ".join(args[2:]))
        elif command == "verify" and len(args) == 1:
            _, errors = verify_files()
            return 1 if errors else 0
        else:
            print("Неверная команда или недостаточно параметров.")
            return 2
        return 0
    except Exception as error:
        print(f"ОШИБКА: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
