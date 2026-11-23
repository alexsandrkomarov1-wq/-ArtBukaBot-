"""Add private media intake registry and immutable blob metadata.

Revision ID: 0005_private_media_intake
Revises: 0004_wide_identifiers
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_private_media_intake"
down_revision = "0004_wide_identifiers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stored_blobs",
        sa.Column("blob_id", sa.String(length=35), primary_key=True),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("detected_mime_type", sa.String(length=120), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("storage_provider", sa.String(length=40), nullable=False, server_default="local-private"),
        sa.Column("storage_object_key", sa.String(length=500), nullable=False),
        sa.Column("storage_state", sa.String(length=24), nullable=False, server_default="quarantined"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("sha256", name="uq_stored_blobs_sha256"),
        sa.UniqueConstraint("storage_object_key", name="uq_stored_blobs_storage_key"),
    )
    op.create_index("ix_stored_blobs_sha256", "stored_blobs", ["sha256"], unique=False)
    op.create_table(
        "archive_items",
        sa.Column("archive_item_id", sa.String(length=35), primary_key=True),
        sa.Column("item_type", sa.String(length=16), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=True),
        sa.Column("record_status", sa.String(length=24), nullable=False, server_default="quarantined"),
        sa.Column("original_blob_id", sa.String(length=35), sa.ForeignKey("stored_blobs.blob_id"), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=34), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("original_blob_id", name="uq_archive_items_original_blob"),
    )
    op.create_index("ix_archive_items_created_by_user_id", "archive_items", ["created_by_user_id"], unique=False)
    op.create_table(
        "archive_entity_links",
        sa.Column("link_id", sa.String(length=35), primary_key=True),
        sa.Column("archive_item_id", sa.String(length=35), sa.ForeignKey("archive_items.archive_item_id"), nullable=False),
        sa.Column("target_entity_type", sa.String(length=24), nullable=False),
        sa.Column("target_entity_id", sa.String(length=40), nullable=False),
        sa.Column("link_role", sa.String(length=32), nullable=False),
        sa.Column("confirmation_status", sa.String(length=16), nullable=False, server_default="confirmed"),
        sa.Column("source_note", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.String(length=34), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "archive_item_id", "target_entity_type", "target_entity_id", "link_role",
            name="uq_archive_entity_link",
        ),
    )
    op.create_index("ix_archive_entity_links_archive_item_id", "archive_entity_links", ["archive_item_id"], unique=False)
    op.create_index("ix_archive_entity_links_target_entity_id", "archive_entity_links", ["target_entity_id"], unique=False)


def downgrade() -> None:
    raise RuntimeError("Private media intake is forward-only; use a reviewed recovery migration.")
