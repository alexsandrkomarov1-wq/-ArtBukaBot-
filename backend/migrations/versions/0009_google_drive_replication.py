"""Add durable Google Drive replica and outbox state.

Revision ID: 0009_google_drive_replication
Revises: 0008_neon_identity_links
"""
from alembic import op
import sqlalchemy as sa

revision = "0009_google_drive_replication"
down_revision = "0008_neon_identity_links"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "google_drive_replicas",
        sa.Column("replica_id", sa.String(35), primary_key=True),
        sa.Column("blob_id", sa.String(35), sa.ForeignKey("stored_blobs.blob_id"), nullable=False),
        sa.Column("drive_file_id", sa.String(160), nullable=True, unique=True),
        sa.Column("folder_id", sa.String(160), nullable=False),
        sa.Column("expected_sha256", sa.String(64), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("state", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lease_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_code", sa.String(80), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("blob_id", name="uq_google_drive_replica_blob"),
    )
    op.create_table(
        "google_drive_outbox",
        sa.Column("job_id", sa.String(35), primary_key=True),
        sa.Column("blob_id", sa.String(35), sa.ForeignKey("stored_blobs.blob_id"), nullable=False, unique=True),
        sa.Column("state", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lease_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_code", sa.String(80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_google_drive_outbox_state", "google_drive_outbox", ["state"])
    op.create_index("ix_google_drive_outbox_available_at", "google_drive_outbox", ["available_at"])


def downgrade() -> None:
    raise RuntimeError("Google Drive replica history is retained; use a reviewed recovery migration.")
