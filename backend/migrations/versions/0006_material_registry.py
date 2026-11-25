"""Add stable MATERIAL-ID identities and original/derivative lineage.

Revision ID: 0006_material_registry
Revises: 0005_private_media_intake
"""
from alembic import op
import sqlalchemy as sa
import secrets

revision = "0006_material_registry"
down_revision = "0005_private_media_intake"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "materials",
        sa.Column("material_id", sa.String(length=35), primary_key=True),
        sa.Column("archive_item_id", sa.String(length=35), sa.ForeignKey("archive_items.archive_item_id"), nullable=False),
        sa.Column("original_material_id", sa.String(length=35), sa.ForeignKey("materials.material_id"), nullable=True),
        sa.Column("material_role", sa.String(length=16), nullable=False, server_default="original"),
        sa.Column("processing_engine", sa.String(length=120), nullable=True),
        sa.Column("source_sha256", sa.String(length=64), nullable=True),
        sa.Column("output_sha256", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_materials_archive_item_id", "materials", ["archive_item_id"], unique=True)
    op.create_index("ix_materials_original_material_id", "materials", ["original_material_id"], unique=False)

    connection = op.get_bind()
    rows = connection.execute(sa.text(
        "SELECT a.archive_item_id, b.sha256, a.created_at "
        "FROM archive_items a JOIN stored_blobs b ON b.blob_id = a.original_blob_id"
    )).mappings().all()
    for row in rows:
        connection.execute(sa.text(
            "INSERT INTO materials "
            "(material_id, archive_item_id, original_material_id, material_role, "
            "processing_engine, source_sha256, output_sha256, created_at) "
            "VALUES (:material_id, :archive_item_id, NULL, 'original', NULL, NULL, :sha256, :created_at)"
        ), {
            "material_id": "M-" + secrets.token_hex(16).upper(),
            "archive_item_id": row["archive_item_id"],
            "sha256": row["sha256"],
            "created_at": row["created_at"],
        })


def downgrade() -> None:
    raise RuntimeError("MATERIAL-ID lineage is permanent; use a reviewed recovery migration.")
