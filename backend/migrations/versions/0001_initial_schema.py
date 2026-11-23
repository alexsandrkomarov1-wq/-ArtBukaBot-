"""Create initial people, relationships and audit tables.

Revision ID: 0001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
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
    op.drop_index("ix_audit_events_entity_id", table_name="audit_events")
    op.drop_index("ix_audit_events_event_type", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index("ix_relationships_to_person_id", table_name="relationships")
    op.drop_index("ix_relationships_from_person_id", table_name="relationships")
    op.drop_table("relationships")
    op.drop_table("people")
