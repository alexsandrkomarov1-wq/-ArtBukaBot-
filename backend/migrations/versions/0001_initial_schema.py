"""Create or adopt the initial people, relationships and audit schema.

Revision ID: 0001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


EXPECTED_COLUMNS = {
    "people": {"person_id", "display_name", "status", "created_at", "updated_at"},
    "relationships": {"relationship_id", "from_person_id", "to_person_id", "relationship_type", "created_at"},
    "audit_events": {"event_id", "event_type", "entity_type", "entity_id", "actor_id", "details", "occurred_at"},
}
EXPECTED_INDEXES = {
    "relationships": {"ix_relationships_from_person_id", "ix_relationships_to_person_id"},
    "audit_events": {"ix_audit_events_event_type", "ix_audit_events_entity_id"},
}


def _adopt_existing_schema() -> bool:
    """Adopt a complete legacy create_all schema without dropping its data."""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing = set(inspector.get_table_names())
    expected_tables = set(EXPECTED_COLUMNS)
    present = existing & expected_tables

    if not present:
        return False
    if present != expected_tables:
        raise RuntimeError(
            "Refusing to migrate a partial legacy schema; expected all core tables "
            f"{sorted(expected_tables)}, found {sorted(present)}"
        )

    for table_name, expected_columns in EXPECTED_COLUMNS.items():
        actual_columns = {column["name"] for column in inspector.get_columns(table_name)}
        if actual_columns != expected_columns:
            raise RuntimeError(
                f"Refusing to adopt incompatible table {table_name}: "
                f"expected columns {sorted(expected_columns)}, found {sorted(actual_columns)}"
            )

    expected_foreign_keys = {
        ("relationships", "from_person_id", "people", "person_id"),
        ("relationships", "to_person_id", "people", "person_id"),
    }
    actual_foreign_keys = set()
    for fk in inspector.get_foreign_keys("relationships"):
        for column, referred_column in zip(fk.get("constrained_columns") or [], fk.get("referred_columns") or []):
            actual_foreign_keys.add((
                "relationships", column, fk.get("referred_table"), referred_column
            ))
    if actual_foreign_keys != expected_foreign_keys:
        raise RuntimeError(
            "Refusing to adopt incompatible relationship foreign keys: "
            f"found {sorted(actual_foreign_keys)}"
        )

    for table_name, expected_indexes in EXPECTED_INDEXES.items():
        actual_indexes = {index["name"] for index in inspector.get_indexes(table_name)}
        if not expected_indexes.issubset(actual_indexes):
            raise RuntimeError(
                f"Refusing to adopt {table_name}: missing indexes "
                f"{sorted(expected_indexes - actual_indexes)}"
            )
    return True


def upgrade() -> None:
    # The previous backend foundation used SQLAlchemy create_all. Existing
    # installations must be versioned in place, never recreated or erased.
    if _adopt_existing_schema():
        return

    op.create_table(
        "people",
        sa.Column("person_id", sa.String(length=14), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("person_id"),
    )
    op.create_table(
        "relationships",
        sa.Column("relationship_id", sa.String(length=14), nullable=False),
        sa.Column("from_person_id", sa.String(length=14), nullable=False),
        sa.Column("to_person_id", sa.String(length=14), nullable=False),
        sa.Column("relationship_type", sa.String(length=60), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["from_person_id"], ["people.person_id"]),
        sa.ForeignKeyConstraint(["to_person_id"], ["people.person_id"]),
        sa.PrimaryKeyConstraint("relationship_id"),
    )
    op.create_index("ix_relationships_from_person_id", "relationships", ["from_person_id"])
    op.create_index("ix_relationships_to_person_id", "relationships", ["to_person_id"])
    op.create_table(
        "audit_events",
        sa.Column("event_id", sa.String(length=14), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("entity_type", sa.String(length=40), nullable=False),
        sa.Column("entity_id", sa.String(length=40), nullable=False),
        sa.Column("actor_id", sa.String(length=80), nullable=True),
        sa.Column("details", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index("ix_audit_events_event_type", "audit_events", ["event_type"])
    op.create_index("ix_audit_events_entity_id", "audit_events", ["entity_id"])


def downgrade() -> None:
    # Reversing this baseline would destroy the core family registry and audit
    # history. A data-preserving rollback must be a separately reviewed migration.
    raise RuntimeError(
        "The initial KOMAROVA_CORE schema migration is irreversible; "
        "restore from a verified backup or use a reviewed forward migration."
    )
