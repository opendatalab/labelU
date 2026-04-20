"""add data_source table and attachment.data_source_id

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if "data_source" not in existing_tables:
        op.create_table(
            "data_source",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(128), nullable=False),
            sa.Column("type", sa.String(32), nullable=False, server_default="S3"),
            sa.Column("endpoint", sa.String(512)),
            sa.Column("region", sa.String(64)),
            sa.Column("bucket", sa.String(256), nullable=False),
            sa.Column("prefix", sa.String(512), server_default=""),
            sa.Column("access_key_id", sa.String(512)),
            sa.Column("secret_access_key", sa.String(1024)),
            sa.Column("path_style", sa.Boolean(), server_default=sa.text("0")),
            sa.Column("use_ssl", sa.Boolean(), server_default=sa.text("1")),
            sa.Column("presign_expire_secs", sa.Integer(), server_default=sa.text("3600")),
            sa.Column("created_by", sa.Integer(), sa.ForeignKey("user.id")),
            sa.Column("updated_by", sa.Integer(), sa.ForeignKey("user.id")),
            sa.Column("created_at", sa.DateTime(timezone=True)),
            sa.Column("updated_at", sa.DateTime(timezone=True)),
            sa.Column("deleted_at", sa.DateTime()),
        )
        op.create_index("ix_data_source_id", "data_source", ["id"])
        op.create_index("ix_data_source_created_by", "data_source", ["created_by"])
        op.create_index("ix_data_source_deleted_at", "data_source", ["deleted_at"])

    existing_columns = [c["name"] for c in inspector.get_columns("task_attachment")]
    if "data_source_id" not in existing_columns:
        with op.batch_alter_table("task_attachment", naming_convention={"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"}) as batch_op:
            batch_op.add_column(
                sa.Column("data_source_id", sa.Integer(), nullable=True)
            )
            batch_op.create_foreign_key(
                "fk_task_attachment_data_source_id_data_source",
                "data_source",
                ["data_source_id"],
                ["id"],
            )
            batch_op.create_index("ix_task_attachment_data_source_id", ["data_source_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_columns = [c["name"] for c in inspector.get_columns("task_attachment")]
    if "data_source_id" in existing_columns:
        with op.batch_alter_table("task_attachment") as batch_op:
            batch_op.drop_index("ix_task_attachment_data_source_id")
            batch_op.drop_column("data_source_id")

    if "data_source" in inspector.get_table_names():
        op.drop_table("data_source")
