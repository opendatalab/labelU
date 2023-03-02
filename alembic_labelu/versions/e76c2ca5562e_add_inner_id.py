"""add inner_id

Revision ID: e76c2ca5562e
Revises: 54fee6a7ecd8
Create Date: 2023-02-28 22:29:31.595257

"""
import imp
import os

from alembic import op
from alembic import context
import sqlalchemy as sa
from sqlalchemy.sql import text

# import alembic_labelu_tools from the absolute path
alembic_labelu_tools = imp.load_source(
    "alembic_labelu_tools",
    (os.getcwd() + "/" + op.get_context().script.dir + "/alembic_labelu_tools.py"),
)

# revision identifiers, used by Alembic.
revision = "e76c2ca5562e"
down_revision = "54fee6a7ecd8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    add inner_id and last_sample_inner_id columns in the task and sample tables
    """
    with context.begin_transaction():
        if not alembic_labelu_tools.column_exist_in_table(
            "task", "last_sample_inner_id"
        ):
            with op.batch_alter_table("task", recreate="always") as batch_op_task:
                batch_op_task.add_column(
                    sa.Column(
                        "last_sample_inner_id",
                        sa.Integer(),
                        nullable=True,
                        comment="The last inner id of sample in a task",
                        server_default=text("0"),
                    ),
                    insert_before="config",
                )
        if not alembic_labelu_tools.column_exist_in_table("task_sample", "inner_id"):
            with op.batch_alter_table(
                "task_sample", recreate="always"
            ) as batch_op_task_sample:
                batch_op_task_sample.add_column(
                    sa.Column(
                        "inner_id",
                        sa.Integer(),
                        nullable=True,
                        comment="sample id in a task",
                    ),
                    insert_after="id",
                )
            op.create_index(
                op.f("ix_task_sample_inner_id"),
                "task_sample",
                ["inner_id"],
                unique=False,
            )

        op.execute(
            "UPDATE task SET last_sample_inner_id=(SELECT sample_number FROM ( SELECT task_id, COUNT(id) AS sample_number FROM task_sample GROUP BY task_id ) task_sample_number WHERE task.id=task_sample_number.task_id )"
        )
        op.execute(
            "UPDATE task_sample SET inner_id=(SELECT newid FROM ( SELECT id, task_id, ROW_NUMBER() OVER (PARTITION BY task_id ORDER BY created_at) AS newid FROM task_sample) tmp_sample_inner_id WHERE task_sample.id=tmp_sample_inner_id.id and task_sample.task_id=tmp_sample_inner_id.task_id)"
        )


def downgrade() -> None:
    """
    delete inner_id and last_sample_inner_id columns in the task and sample tables
    """
    op.drop_index(op.f("ix_task_sample_inner_id"), table_name="task_sample")
    op.drop_column("task_sample", "inner_id")
    op.drop_column("task", "last_sample_inner_id")
