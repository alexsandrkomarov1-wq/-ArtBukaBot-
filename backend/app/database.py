from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool


class Base(DeclarativeBase):
    pass


def normalize_database_url(database_url: str | None = None) -> str:
    """Normalize provider URLs to the installed PostgreSQL driver.

    Neon supplies postgresql:// URLs. The project deliberately uses psycopg 3
    rather than relying on an implicitly installed psycopg2 driver.
    """
    raw = database_url or os.getenv("DATABASE_URL", "sqlite:///./komarova_core.db")
    raw = raw.strip()
    if raw.startswith("postgres://"):
        return "postgresql+psycopg://" + raw[len("postgres://"):]
    if raw.startswith("postgresql://"):
        return "postgresql+psycopg://" + raw[len("postgresql://"):]
    return raw


def build_engine(database_url: str | None = None) -> Engine:
    url = normalize_database_url(database_url)
    options: dict = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        options["connect_args"] = {"check_same_thread": False}
    elif url.startswith("postgresql+psycopg://"):
        # Serverless instances should not retain idle connections between invocations.
        # Use Neon's pooled connection string in Vercel/serverless deployments.
        is_serverless = any(os.getenv(name) for name in (
            "VERCEL", "AWS_LAMBDA_FUNCTION_NAME", "FUNCTIONS_WORKER_RUNTIME",
        ))
        if is_serverless:
            options["poolclass"] = NullPool
        else:
            options["pool_size"] = int(os.getenv("CORE_DB_POOL_SIZE", "3"))
            options["max_overflow"] = int(os.getenv("CORE_DB_MAX_OVERFLOW", "2"))
            options["pool_recycle"] = 300
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


def verify_migrations_current(engine: Engine) -> None:
    """Fail fast when the database is not at the code's migration head."""
    project_root = Path(__file__).resolve().parents[2]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "backend" / "migrations"))
    config.set_main_option("prepend_sys_path", str(project_root))
    expected_revision = ScriptDirectory.from_config(config).get_current_head()
    with engine.connect() as connection:
        current_revision = MigrationContext.configure(connection).get_current_revision()
    if current_revision != expected_revision:
        raise RuntimeError(
            "Database schema is not at the current migration head. "
            "Run 'python -m backend.app.migrate' once before starting API workers."
        )


def session_dependency(factory) -> Generator[Session, None, None]:
    session = factory()
    try:
        yield session
    finally:
        session.close()
