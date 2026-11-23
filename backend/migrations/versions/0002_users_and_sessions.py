"""Add user accounts and revocable authentication sessions.

Revision ID: 0002_users_sessions
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_users_sessions"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(length=14), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=24), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=False)
    op.create_table(
        "auth_sessions",
        sa.Column("session_id", sa.String(length=14), nullable=False),
        sa.Column("user_id", sa.String(length=14), nullable=False),
        sa.Column("token_jti", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("session_id"),
        sa.UniqueConstraint("token_jti"),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"], unique=False)
    op.create_index("ix_auth_sessions_token_jti", "auth_sessions", ["token_jti"], unique=False)


def downgrade() -> None:
    raise RuntimeError("User-account migration is forward-only; use a reviewed recovery procedure.")
