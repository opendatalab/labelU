"""add media and pre_annotation

Revision ID: bc8fcb35b66b
Revises: 1b174ca5159a
Create Date: 2024-02-07 15:58:30.618151

"""
import imp
import json
import os

from alembic import context, op
import sqlalchemy as sa
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

Base = automap_base()


# revision identifiers, used by Alembic.
revision = 'bc8fcb35b66b'
down_revision = '1b174ca5159a'
branch_labels = None
depends_on = None

# import alembic_labelu_tools from the absolute path
alembic_labelu_tools = imp.load_source(
    "alembic_labelu_tools",
    (
        os.path.join(
            os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
            "alembic_labelu_tools.py",
        )
    ),
)

def upgrade() -> None:
    bind = op.get_bind()
    Base.prepare(autoload_with=bind, reflect=True)
    task_sample = Base.classes.task_sample
    # make a session
    Session = sessionmaker(bind=bind)
    session = Session()
    
    with context.begin_transaction():
        # Update the task_sample table
        if not alembic_labelu_tools.column_exist_in_table(
            "task_sample", "media_id"
        ):
            with op.batch_alter_table('task_sample', recreate="always") as batch_op:
                batch_op.add_column(
                    sa.Column(
                        "media_id",
                        sa.Integer(),
                        sa.ForeignKey("task_attachment.id", name="fk_media_id"),
                        index=True,
                        comment="media id",
                    ),
                )
                batch_op.add_column(
                    sa.Column(
                        "pre_annotation_id",
                        sa.Integer(),
                        sa.ForeignKey("task_attachment.id", name="fk_pre_annotation_id"),
                        index=True,
                        comment="pre annotation id",
                    ),
                )
        
        # Update the task_attachment table
        if not alembic_labelu_tools.column_exist_in_table("task_attachment", "filename"):
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
            'SELECT id, config FROM task WHERE config IS NOT NULL AND config != ""'
        )
        
        for task_item in task_items:
            task_id = task_item[0]
            task_samples = session.execute(
                f"SELECT id, data, annotated_count FROM task_sample WHERE task_id={task_id}"
            )

            for task_sample in task_samples:
                task_sample_id = task_sample[0]
                task_sample_data = task_sample[1]
                task_sample_data = json.loads(task_sample_data)
                fileNames = task_sample_data.get("fileNames")
                # First key is media_id
                if fileNames:
                    media_id = next(iter(task_sample_data.get("fileNames").keys()), None)
                    filename = task_sample_data.get("fileNames").get(media_id)
                    url = task_sample_data.get("urls").get(media_id)

                    # Update the task_sample table
                    session.execute(
                        f"UPDATE task_sample SET media_id={media_id}, pre_annotation_id=NULL WHERE id={task_sample_id}"
                    )
                    # Update the task_attachment table
                    session.execute(
                        f"UPDATE task_attachment SET filename='{filename}', url='{url}' WHERE id={media_id}"
                    )
        

def downgrade() -> None:
    with op.batch_alter_table('task_sample') as batch_op:
        batch_op.drop_column('media_id')
        batch_op.drop_column('pre_annotation_id')
