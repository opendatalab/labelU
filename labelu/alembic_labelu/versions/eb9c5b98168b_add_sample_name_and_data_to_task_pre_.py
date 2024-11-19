"""add_sample_name_and_data_to_task_pre_annotation

1. Add sample_name column to task_pre_annotation table.
2. Read jsonl file content and store it in data column of task_pre_annotation table.

Revision ID: eb9c5b98168b
Revises: bc8fcb35b66b
Create Date: 2024-11-13 14:08:09.374271

"""
import json
from typing import List
from alembic import op, context
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import select
from labelu.internal.common.config import settings

from labelu.internal.domain.models.pre_annotation import TaskPreAnnotation
from labelu.internal.adapter.persistence import crud_attachment

Base = automap_base()


# revision identifiers, used by Alembic.
revision = 'eb9c5b98168b'
down_revision = 'bc8fcb35b66b'
branch_labels = None
depends_on = None

def index_exists(bind, table_name, index_name):
    inspector = sa.inspect(bind)
    indexes = inspector.get_indexes(table_name)
    for index in indexes:
        if index['name'] == index_name:
            return True
    return False

def read_jsonl_file(db: Session, file_id: int) -> List[dict]:
    attachment = crud_attachment.get(db, file_id)
    if attachment is None:
        return []

    attachment_path = attachment.path
    file_full_path = settings.MEDIA_ROOT.joinpath(attachment_path.lstrip("/"))
    
    # check if the file exists
    if not file_full_path.exists() or not attachment.filename.endswith('.jsonl'):
        return []

    
    with open(file_full_path, "r", encoding="utf-8") as f:
        data = f.readlines()

    parsed_data = [json.loads(line) for line in data]
    return parsed_data

def upgrade() -> None:
    bind = op.get_bind()
    Base.prepare(autoload_with=bind, reflect=True)
    # make a session
    SessionMade = sessionmaker(bind=bind)
    session = SessionMade()
    
    try:
        with context.begin_transaction():
            # add column sample_name, check if the column exists
            if not hasattr(Base.classes.task_pre_annotation, "sample_name"):
                op.add_column(
                    "task_pre_annotation",
                    sa.Column("sample_name", sa.String(255), index=True, comment="One of the sample names of the task"),
                )
            
            # create index, check if the index exists
            if not index_exists(bind, "task_pre_annotation", "idx_pre_annotation_sample_name"):
                op.create_index("idx_pre_annotation_sample_name", "task_pre_annotation", ["sample_name"])
                
            # create task_pre_annotation
            exist_task_pre_annotations = session.execute(
                select([Base.classes.task_pre_annotation])
            ).scalars().all()
            
            for task_pre_annotation in exist_task_pre_annotations:
                file_id = task_pre_annotation.file_id
                jsonl_contents = read_jsonl_file(session, file_id)
                
                # create new task_pre_annotation
                for jsonl_content in jsonl_contents:
                    sample_name = jsonl_content.get("sample_name")
                    query = select(Base.classes.task_attachment).where(
                        Base.classes.task_attachment.task_id == task_pre_annotation.task_id,
                        # filename include sample_name, full name is xxxxxxxxx-sample_name.png, shot name is sample_name.png
                        Base.classes.task_attachment.filename.contains(sample_name),
                    )
                    sample_file = session.execute(query).scalars().first()
                    new_task_pre_annotation = TaskPreAnnotation(
                        task_id=task_pre_annotation.task_id,
                        # full file name
                        sample_name=sample_file.filename if sample_file else None,
                        file_id=file_id,
                        created_by=task_pre_annotation.created_by,
                        updated_by=task_pre_annotation.updated_by,
                        data=json.dumps(jsonl_content),
                    )
                    session.add(new_task_pre_annotation)
            
            # remove existing task_pre_annotation
            for task_pre_annotation in exist_task_pre_annotations:
                session.delete(task_pre_annotation)
                
            # commit 
            session.commit()
            
    except Exception as e:
        session.rollback()
        raise e
    
    finally:
        session.close()


def downgrade() -> None:
    bind = op.get_bind()
    Base.prepare(autoload_with=bind, reflect=True)
    SessionMade = sessionmaker(bind=bind)
    session = SessionMade()
    
    try:
        with context.begin_transaction():
            # remove new task_pre_annotation
            new_task_pre_annotations = session.query(Base.classes.task_pre_annotation).filter(
                Base.classes.task_pre_annotation.sample_name.isnot(None)
            ).all()
            
            for task_pre_annotation in new_task_pre_annotations:
                session.delete(task_pre_annotation)
            
            # restore old task_pre_annotation
            old_task_pre_annotations = session.query(TaskPreAnnotation).filter(
                TaskPreAnnotation.sample_name.isnot(None)
            ).all()
            
            for task_pre_annotation in old_task_pre_annotations:
                restored_task_pre_annotation = Base.classes.task_pre_annotation(
                    task_id=task_pre_annotation.task_id,
                    file_id=task_pre_annotation.file_id,
                    created_by=task_pre_annotation.created_by,
                    updated_by=task_pre_annotation.updated_by,
                    data=task_pre_annotation.data,
                )
                session.add(restored_task_pre_annotation)
            
            # drop index
            if index_exists(bind, "task_pre_annotation", "idx_pre_annotation_sample_name"):
                op.drop_index("idx_pre_annotation_sample_name", table_name="task_pre_annotation")
            
            # drop column
            if hasattr(Base.classes.task_pre_annotation, "sample_name"):
                op.drop_column("task_pre_annotation", "sample_name")
            
            # commit
            session.commit()
    
    except Exception as e:
        session.rollback()
        raise e
    
    finally:
        session.close()