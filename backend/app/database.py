from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def build_engine(database_url: str | None = None) -> Engine:
    url = database_url or os.getenv("DATABASE_URL", "sqlite:///./komarova_core.db")
    options: dict = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        options["connect_args"] = {"check_same_thread": False}
    return create_engine(url, **options)


def build_session_factory(engine: Engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def run_migrations(engine: Engine) -> None:
    project_root = Path(__file__).resolve().parents[2]
    config = Config(str(project_root / "alembic.ini"))
    # Both Alembic paths must be absolute: services may start outside the repo root.
    config.set_main_option("script_location", str(project_root / "backend" / "migrations"))
    config.set_main_option("prepend_sys_path", str(project_root))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")


def session_dependency(factory) -> Generator[Session, None, None]:
    session = factory()
    try:
        yield session
    finally:
        session.close()
