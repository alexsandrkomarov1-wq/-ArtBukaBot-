import hashlib
import importlib.util
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "komarova_file_engine.py"
spec = importlib.util.spec_from_file_location("komarova_file_engine", MODULE_PATH)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


def make_db(path: Path):
    with sqlite3.connect(path) as db:
        db.execute("""CREATE TABLE materials (
            material_id TEXT PRIMARY KEY, file_name TEXT NOT NULL, sha256 TEXT NOT NULL,
            received_time TEXT NOT NULL, geo_status TEXT NOT NULL, file_type TEXT NOT NULL,
            extension TEXT NOT NULL, original_path TEXT NOT NULL, stored_path TEXT,
            file_size INTEGER NOT NULL, mime_type TEXT, file_status TEXT NOT NULL
        )""")


def configure(tmp_path, monkeypatch):
    db_path = tmp_path / "registry.sqlite3"
    make_db(db_path)
    monkeypatch.setattr(engine, "DB_FILE", db_path)
    monkeypatch.setattr(engine, "STORAGE", tmp_path / "storage")
    monkeypatch.setattr(engine, "LOG_DIR", tmp_path / "logs")
    return db_path


def test_import_registers_verified_copy_and_preserves_source(tmp_path, monkeypatch):
    db_path = configure(tmp_path, monkeypatch)
    source = tmp_path / "family-photo.jpg"
    source.write_bytes(b"photo-bytes-123")
    original = source.read_bytes()
    material_id = engine.import_file(source)
    with sqlite3.connect(db_path) as db:
        row = db.execute("SELECT material_id,file_name,sha256,original_path,stored_path,file_size,file_status FROM materials").fetchone()
    assert row[0] == material_id
    assert row[1] == source.name
    assert row[2] == hashlib.sha256(original).hexdigest()
    assert row[3] == str(source.resolve())
    assert Path(row[4]).read_bytes() == original
    assert row[5] == len(original)
    assert row[6] == "verified"
    assert source.read_bytes() == original
    assert (tmp_path / "logs" / "file_engine.log").is_file()


def test_duplicate_content_reuses_id_and_does_not_create_second_record(tmp_path, monkeypatch):
    db_path = configure(tmp_path, monkeypatch)
    first = tmp_path / "one.jpg"
    second = tmp_path / "two.jpg"
    first.write_bytes(b"same-payload")
    second.write_bytes(b"same-payload")
    first_id = engine.import_file(first)
    second_id = engine.import_file(second)
    assert first_id == second_id
    with sqlite3.connect(db_path) as db:
        assert db.execute("SELECT COUNT(*) FROM materials").fetchone()[0] == 1
    assert len(list((tmp_path / "storage").rglob("*.jpg"))) == 1


def test_missing_archive_copy_is_repaired_without_changing_material_id(tmp_path, monkeypatch):
    db_path = configure(tmp_path, monkeypatch)
    source = tmp_path / "repair.png"
    source.write_bytes(b"repair-me")
    material_id = engine.import_file(source)
    with sqlite3.connect(db_path) as db:
        stored_path = db.execute("SELECT stored_path FROM materials WHERE material_id=?", (material_id,)).fetchone()[0]
    Path(stored_path).unlink()
    repaired_id = engine.import_file(source)
    assert repaired_id == material_id
    assert Path(stored_path).read_bytes() == source.read_bytes()


def test_verify_checks_hash_and_size(tmp_path, monkeypatch):
    db_path = configure(tmp_path, monkeypatch)
    source = tmp_path / "clip.mp4"
    source.write_bytes(b"video-fixture")
    engine.import_file(source)
    assert engine.verify_files() == (1, 0)
    with sqlite3.connect(db_path) as db:
        stored_path = db.execute("SELECT stored_path FROM materials").fetchone()[0]
    Path(stored_path).write_bytes(b"tampered")
    assert engine.verify_files() == (0, 1)


def test_import_requires_geo_status_and_does_not_create_partial_storage(tmp_path, monkeypatch):
    db_path = tmp_path / "legacy.sqlite3"
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE TABLE materials (material_id TEXT PRIMARY KEY)")
    monkeypatch.setattr(engine, "DB_FILE", db_path)
    monkeypatch.setattr(engine, "STORAGE", tmp_path / "storage")
    monkeypatch.setattr(engine, "LOG_DIR", tmp_path / "logs")
    source = tmp_path / "x.jpg"
    source.write_bytes(b"x")
    try:
        engine.prepare()
    except RuntimeError as exc:
        assert "geo_status" in str(exc) or "file_name" in str(exc)
    else:
        raise AssertionError("incompatible schema must be rejected")
    assert not (tmp_path / "storage").exists()


def test_unsupported_extension_is_rejected(tmp_path, monkeypatch):
    configure(tmp_path, monkeypatch)
    source = tmp_path / "script.exe"
    source.write_bytes(b"not allowed")
    try:
        engine.import_file(source)
    except ValueError as exc:
        assert "не поддерживается" in str(exc)
    else:
        raise AssertionError("unsupported extension must fail")


def test_export_refuses_overwrite_and_verifies_copy(tmp_path, monkeypatch):
    configure(tmp_path, monkeypatch)
    source = tmp_path / "report.pdf"
    source.write_bytes(b"pdf-fixture")
    material_id = engine.import_file(source)
    destination = tmp_path / "export" / "copy.pdf"
    exported = engine.export_file(material_id, destination)
    assert exported.read_bytes() == source.read_bytes()
    try:
        engine.export_file(material_id, destination)
    except FileExistsError:
        pass
    else:
        raise AssertionError("export must not overwrite existing destination")


def test_log_failure_does_not_remove_committed_file_or_registry_row(tmp_path, monkeypatch):
    db_path = configure(tmp_path, monkeypatch)
    source = tmp_path / "log-failure.jpg"
    source.write_bytes(b"keep-registered-file")
    def fail_log(_message):
        raise OSError("simulated log disk failure")
    monkeypatch.setattr(engine, "log", fail_log)
    material_id = engine.import_file(source)
    with sqlite3.connect(db_path) as db:
        stored_path = db.execute(
            "SELECT stored_path FROM materials WHERE material_id=?", (material_id,)
        ).fetchone()[0]
    assert Path(stored_path).is_file()
    assert Path(stored_path).read_bytes() == source.read_bytes()


def test_corrupted_archive_is_preserved_and_reimported_to_new_path(tmp_path, monkeypatch):
    db_path = configure(tmp_path, monkeypatch)
    source = tmp_path / "recovery.jpg"
    source.write_bytes(b"original-photo-payload")
    material_id = engine.import_file(source)

    with sqlite3.connect(db_path) as db:
        old_stored_path = Path(db.execute(
            "SELECT stored_path FROM materials WHERE material_id=?", (material_id,)
        ).fetchone()[0])

    old_stored_path.write_bytes(b"corrupted-archive-evidence")
    repaired_id = engine.import_file(source)

    with sqlite3.connect(db_path) as db:
        new_stored_path = Path(db.execute(
            "SELECT stored_path FROM materials WHERE material_id=?", (material_id,)
        ).fetchone()[0])

    assert repaired_id == material_id
    assert old_stored_path.read_bytes() == b"corrupted-archive-evidence"
    assert new_stored_path != old_stored_path
    assert new_stored_path.read_bytes() == source.read_bytes()
    assert engine.verify_files() == (1, 0)
    log_text = (tmp_path / "logs" / "file_engine.log").read_text(encoding="utf-8")
    assert "RECOVERY" in log_text
