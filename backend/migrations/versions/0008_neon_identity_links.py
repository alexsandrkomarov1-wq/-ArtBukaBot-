"""Add explicit Neon Auth identity mappings without replacing local accounts.

Revision ID: 0008_neon_identity_links
Revises: 0007_entity_graph
"""
from alembic import op
import sqlalchemy as sa

revision = "0008_neon_identity_links"
down_revision = "0007_entity_graph"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "external_identities",
        sa.Column("identity_id", sa.String(length=35), primary_key=True),
        sa.Column("provider", sa.String(length=24), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.String(length=34), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("provider", "subject", name="uq_external_identity_provider_subject"),
        sa.UniqueConstraint("provider", "user_id", name="uq_external_identity_provider_user"),
    )
    op.create_index("ix_external_identities_user_id", "external_identities", ["user_id"])


def downgrade() -> None:
    raise RuntimeError("External identity links are security-critical; use a reviewed recovery migration.")
