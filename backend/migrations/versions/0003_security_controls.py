"""Add serialized security state and persistent login throttling.

Revision ID: 0003_security_controls
Revises: 0002_users_and_sessions
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_security_controls"
down_revision = "0002_users_and_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "system_state",
        sa.Column("state_key", sa.String(length=80), primary_key=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_table(
        "login_attempts",
        sa.Column("attempt_key", sa.String(length=64), primary_key=True),
        sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(sa.text(
        "INSERT INTO system_state (state_key, version) VALUES ('security_admin', 0)"
    ))


def downgrade() -> None:
    op.drop_table("login_attempts")
    op.drop_table("system_state")
