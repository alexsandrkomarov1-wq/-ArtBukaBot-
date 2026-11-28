"""Add provider-neutral cloud replica queue.

Revision ID: 0010_cloud_replicas
Revises: 0009_google_drive_replication
"""
from alembic import op
import sqlalchemy as sa

revision = "0010_cloud_replicas"
down_revision = "0009_google_drive_replication"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cloud_replicas",
        sa.Column("replica_id", sa.String(35), primary_key=True),
        sa.Column("blob_id", sa.String(35), sa.ForeignKey("stored_blobs.blob_id"), nullable=False),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("remote_id", sa.String(500), nullable=True),
        sa.Column("expected_sha256", sa.String(64), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("state", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lease_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_code", sa.String(100), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("blob_id", "provider", name="uq_cloud_replica_blob_provider"),
        sa.UniqueConstraint("provider", "remote_id", name="uq_cloud_replica_remote_id"),
    )
    op.create_index("ix_cloud_replicas_blob_id", "cloud_replicas", ["blob_id"])
    op.create_index("ix_cloud_replicas_provider", "cloud_replicas", ["provider"])
    op.create_index("ix_cloud_replicas_state", "cloud_replicas", ["state"])
    op.create_index("ix_cloud_replicas_next_attempt_at", "cloud_replicas", ["next_attempt_at"])


def downgrade() -> None:
    raise RuntimeError("Cloud replica history is retained; use a reviewed recovery migration.")
