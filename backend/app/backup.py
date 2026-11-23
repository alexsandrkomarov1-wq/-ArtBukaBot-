"""SQLite online backup and verified restore helpers.

These helpers are deliberately explicit and never overwrite the source database.
"""
from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path
from sqlalchemy.engine import Engine


def _sqlite_connection(engine: Engine):
    if engine.dialect.name != "sqlite":
        raise ValueError("This backup helper currently supports SQLite only")
    raw = engine.raw_connection()
    return raw, raw.driver_connection


def _check_integrity(connection: sqlite3.Connection) -> None:
    result = connection.execute("PRAGMA integrity_check").fetchone()
    if not result or result[0] != "ok":
        raise RuntimeError(f"SQLite integrity_check failed: {result[0] if result else 'no result'}")


def backup_database(engine: Engine, destination: str | Path) -> Path:
    target = Path(destination).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError(f"Backup destination already exists: {target}")
    raw, source = _sqlite_connection(engine)
    try:
        with sqlite3.connect(target) as backup:
            source.backup(backup)
            _check_integrity(backup)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    finally:
        raw.close()
    return target


def restore_database(backup_path: str | Path, destination: str | Path) -> Path:
    source_path = Path(backup_path).resolve()
    target = Path(destination).resolve()
    if source_path == target:
        raise ValueError("Restore destination must differ from backup source")
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".restore", dir=target.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        with sqlite3.connect(source_path) as source, sqlite3.connect(temporary) as restored:
            _check_integrity(source)
            source.backup(restored)
            _check_integrity(restored)
        os.replace(temporary, target)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return target
