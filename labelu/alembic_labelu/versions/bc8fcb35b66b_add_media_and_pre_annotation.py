"""add file and pre_annotation

Revision ID: bc8fcb35b66b
Revises: 1b174ca5159a
Create Date: 2024-02-07 15:58:30.618151

"""
import json
import os

from alembic import context, op
import sqlalchemy as sa
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from labelu.internal.common.config import settings
from labelu.alembic_labelu.alembic_labelu_tools import table_exist, column_exist_in_table

Base = automap_base()


# revision identifiers, used by Alembic.
revision = 'bc8fcb35b66b'
down_revision = '1b174ca5159a'
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    Base.prepare(autoload_with=bind, reflect=True)
    task_sample = Base.classes.task_sample
    # make a session
    Session = sessionmaker(bind=bind)
    session = Session()
    
    try:
    
        with context.begin_transaction():
            # Create a new table task_pre_annotation
            if not table_exist("task_pre_annotation"):
                op.create_table(
                    "task_pre_annotation",
                    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, index=True),
                    sa.Column("task_id", sa.Integer, sa.ForeignKey("task.id"), index=True),
                    sa.Column("file_id", sa.Integer, sa.ForeignKey("task_attachment.id"), index=True),
                    # json 字符串
                    sa.Column("data", sa.Text, comment="task sample pre annotation result"),
                    sa.Column("created_by", sa.Integer, sa.ForeignKey("user.id"), index=True),
                    sa.Column("updated_by", sa.Integer, sa.ForeignKey("user.id")),
                    sa.Column(
                        "created_at",
                        sa.DateTime,
                        default=sa.func.now(),
                        comment="Time a task sample result was created",
                    ),
                    sa.Column(
                        "updated_at",
                        sa.DateTime,
                        default=sa.func.now(),
                        onupdate=sa.func.now(),
                        comment="Last time a task sample result was updated",
                    ),
                    sa.Column(
                        "deleted_at",
                        sa.DateTime,
                        index=True,
                        comment="Task delete time",
                    ),
                )
            # Update the task_sample table
            if not column_exist_in_table(
                "task_sample", "file_id"
            ):
                with op.batch_alter_table('task_sample', recreate="always") as batch_op:
                    batch_op.add_column(
                        sa.Column(
                            "file_id",
                            sa.Integer(),
                            sa.ForeignKey("task_attachment.id", name="fk_file_id"),
                            index=True,
                            comment="file id",
                        ),
                    )
            
            # Update the task_attachment table
            if not column_exist_in_table("task_attachment", "filename"):
                with op.batch_alter_table("task_attachment", recreate="always") as batch_op_task_attachment:
                    batch_op_task_attachment.add_column(
                        sa.Column(
                            "filename",
                            sa.String(256),
                            comment="file name",
                        ),
                    )
                    batch_op_task_attachment.add_column(
                        sa.Column(
                            "url",
                            sa.String(256),
                            comment="file url",
                        ),
                    )
                            
            # Update existing data in the task_sample table
            task_items = session.execute(
                'SELECT id, config FROM task'
            )
            
            # Update the task_attachment table
            attachments = session.execute(
                'SELECT id, path FROM task_attachment'
            )
            
            for attachment in attachments:
                attachment_id = attachment[0]
                attachment_path = attachment[1]
                filename = os.path.basename(attachment_path)
                url = f"{settings.API_V1_STR}/tasks/attachment/{attachment_path}"
                
                if filename:
                    session.execute(
                        f"UPDATE task_attachment SET filename='{filename}', url='{url}' WHERE id={attachment_id}"
                    )
            
            if column_exist_in_table("task_sample", "task_attachment_ids"):
                for task_item in task_items:
                    task_id = task_item[0]
                    task_samples = session.execute(
                        f"SELECT id, task_attachment_ids FROM task_sample WHERE task_id={task_id}"
                    )

                    for task_sample in task_samples:
                        task_sample_id = task_sample[0]
                        attachment_ids = json.loads(task_sample[1])
                        # attachment_ids 存储的是字符串[id1, id2, id3]，需要转换成数组
                        file_id = attachment_ids[0]
                        
                        if not file_id:
                            continue
                        
                        attachment = session.execute(
                            f"SELECT id, path FROM task_attachment WHERE id={file_id}"
                        )
                        attachment_path = list(attachment)[0][1]
                        
                        if attachment_path:
                            # Update the task_sample table
                            session.execute(
                                f"UPDATE task_sample SET file_id={file_id} WHERE id={task_sample_id}"
                            )
                
            session.commit()
    
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def downgrade() -> None:
    op.drop_table("task_pre_annotation")
    with op.batch_alter_table('task_sample') as batch_op:
        batch_op.drop_column('file_id')
