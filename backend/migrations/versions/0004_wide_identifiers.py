"""Widen generated identifiers without changing existing identifier values.

Revision ID: 0004_wide_identifiers
Revises: 0003_security_controls
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_wide_identifiers"
down_revision = "0003_security_controls"
branch_labels = None
depends_on = None

NEW_ID_LENGTH = 34


def _widen_columns(table_name: str, column_names: tuple[str, ...]) -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"]: column for column in inspector.get_columns(table_name)}
    changes = [
        name for name in column_names
        if getattr(columns[name]["type"], "length", None) != NEW_ID_LENGTH
    ]
    if not changes:
        return
    with op.batch_alter_table(table_name) as batch_op:
        for name in changes:
            batch_op.alter_column(
                name,
                existing_type=columns[name]["type"],
                type_=sa.String(length=NEW_ID_LENGTH),
                existing_nullable=columns[name]["nullable"],
            )


def upgrade() -> None:
    # Alter referencing columns before their referenced primary keys. Batch
    # mode keeps SQLite supported; PostgreSQL receives normal ALTER COLUMN DDL.
    _widen_columns("relationships", ("relationship_id", "from_person_id", "to_person_id"))
    _widen_columns("auth_sessions", ("session_id", "user_id"))
    _widen_columns("audit_events", ("event_id",))
    _widen_columns("users", ("user_id",))
    _widen_columns("people", ("person_id",))


def downgrade() -> None:
    raise RuntimeError(
        "Identifier widening is forward-only. Shortening identifiers can truncate "
        "or invalidate permanent references; restore only through a reviewed recovery plan."
    )
