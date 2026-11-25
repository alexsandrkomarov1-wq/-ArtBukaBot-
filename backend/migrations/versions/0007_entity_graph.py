"""Add event, place, visit and cross-entity registries.

Revision ID: 0007_entity_graph
Revises: 0006_material_registry
"""
from alembic import op
import sqlalchemy as sa

revision = "0007_entity_graph"
down_revision = "0006_material_registry"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("event_id", sa.String(35), primary_key=True),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.Column("created_by_user_id", sa.String(34), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_events_occurred_at", "events", ["occurred_at"])
    op.create_index("ix_events_created_by_user_id", "events", ["created_by_user_id"])

    op.create_table(
        "places",
        sa.Column("place_id", sa.String(35), primary_key=True),
        sa.Column("name", sa.String(240), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("created_by_user_id", sa.String(34), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("(latitude IS NULL AND longitude IS NULL) OR (latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180)", name="ck_places_coordinates"),
    )
    op.create_index("ix_places_name", "places", ["name"])
    op.create_index("ix_places_created_by_user_id", "places", ["created_by_user_id"])

    op.create_table(
        "place_visits",
        sa.Column("visit_id", sa.String(35), primary_key=True),
        sa.Column("place_id", sa.String(35), sa.ForeignKey("places.place_id"), nullable=False),
        sa.Column("visited_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.String(34), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_place_visits_place_id", "place_visits", ["place_id"])
    op.create_index("ix_place_visits_created_by_user_id", "place_visits", ["created_by_user_id"])

    op.create_table(
        "entity_links",
        sa.Column("link_id", sa.String(35), primary_key=True),
        sa.Column("source_type", sa.String(16), nullable=False),
        sa.Column("source_id", sa.String(40), nullable=False),
        sa.Column("target_type", sa.String(16), nullable=False),
        sa.Column("target_id", sa.String(40), nullable=False),
        sa.Column("relationship_type", sa.String(48), nullable=False),
        sa.Column("created_by_user_id", sa.String(34), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("source_type", "source_id", "target_type", "target_id", "relationship_type", name="uq_entity_link_identity"),
    )
    for column in ("source_type", "source_id", "target_type", "target_id"):
        op.create_index(f"ix_entity_links_{column}", "entity_links", [column])


def downgrade() -> None:
    raise RuntimeError("The shared entity graph is forward-only; use a reviewed recovery migration.")
