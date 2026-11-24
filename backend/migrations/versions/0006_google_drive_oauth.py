"""Add encrypted per-user Google Drive OAuth account connections.

Revision ID: 0006_google_drive_oauth
Revises: 0005_private_media_intake
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_google_drive_oauth"
down_revision = "0005_private_media_intake"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "google_oauth_states",
        sa.Column("state_hash", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=34), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_google_oauth_states_user_id", "google_oauth_states", ["user_id"])

    op.create_table(
        "google_drive_accounts",
        sa.Column("drive_account_id", sa.String(length=35), primary_key=True),
        sa.Column("user_id", sa.String(length=34), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("google_user_id", sa.String(length=255), nullable=False, unique=True),
        sa.Column("email_address", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("refresh_token_ciphertext", sa.Text(), nullable=False),
        sa.Column("granted_scopes", sa.Text(), nullable=False),
        sa.Column("quota_limit_bytes", sa.BigInteger(), nullable=True),
        sa.Column("quota_usage_bytes", sa.BigInteger(), nullable=True),
        sa.Column("quota_usage_in_drive_bytes", sa.BigInteger(), nullable=True),
        sa.Column("quota_usage_in_trash_bytes", sa.BigInteger(), nullable=True),
        sa.Column("last_quota_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id", name="uq_google_drive_accounts_user_id"),
    )
    op.create_index("ix_google_drive_accounts_google_user_id", "google_drive_accounts", ["google_user_id"], unique=True)


def downgrade() -> None:
    raise RuntimeError("Google Drive OAuth data is security-sensitive; use a reviewed forward migration.")
