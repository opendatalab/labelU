"""add_pre_annotation_detail

1. 建立 TaskPreAnnotationDetail 表
2. 将 现有的 预标注jsonl中的记录解析导入到 TaskPreAnnotationDetail 表中
3. 给现有的TaskPreAnnotation表增加filename一列，并将Attachment中的filename的数据添加到TaskPreAnnotation表中
4. 删除 TaskPreAnnotation 表中的 file_id、file、updater、updated_by、updated_at 字段


Revision ID: 4f44b0879945
Revises: bc8fcb35b66b
Create Date: 2024-06-06 16:17:55.458758

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker


from datetime import datetime
import json
from labelu.internal.common.config import settings


# revision identifiers, used by Alembic.
revision = '4f44b0879945'
down_revision = 'bc8fcb35b66b'
branch_labels = None
depends_on = None

Base = automap_base()

def upgrade() -> None:
    # 1. Create new table task_pre_annotation_detail, init_table run first, so we can use the table directly
    
    # 2. Parse and import the records in the existing pre-annotation jsonl into the TaskPreAnnotationDetail table
    bind = op.get_bind()
    Base.prepare(autoload_with=bind, reflect=True)
    # make a session
    Session = sessionmaker(bind=bind)
    session = Session()
    
    task_pre_annotations = session.execute(
        'SELECT id, file_id, task_id, created_by FROM task_pre_annotation WHERE deleted_at IS NULL'
    ).fetchall()
    attachments = session.execute('SELECT id, path, filename FROM task_attachment WHERE deleted_at IS NULL').fetchall()
    attachments_dict = {item.id: item for item in attachments}
    
    for pre_item in task_pre_annotations:
        attachment = attachments_dict.get(pre_item.file_id)
        
        if not attachment or not attachment.path or not attachment.path.endswith(".jsonl"):
            continue
        
        full_path = settings.MEDIA_ROOT.joinpath(attachment.path.lstrip("/"))
        
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                data = f.readlines()
        except FileNotFoundError:
            continue

        for line in data:
            item = json.loads(line)
            
            detail = {
                'task_id': pre_item.task_id,
                'pre_annotation_id': pre_item.id,
                'sample_name': item.get('sample_name'),
                'data': json.dumps(item),
                'created_by': pre_item.created_by,
                'created_at': datetime.now(),
            }
            session.execute(
                sa.text('INSERT INTO task_pre_annotation_detail (task_id, pre_annotation_id, sample_name, data, created_by, created_at) VALUES (:task_id, :pre_annotation_id, :sample_name, :data, :created_by, :created_at)'),
                detail
            )
    
    session.commit()
    
    # transfer the data from the old table to the new table task_pre_annotation_file
    op.execute('''
        INSERT INTO task_pre_annotation_file (id, task_id, created_by, created_at, deleted_at)
        SELECT id, task_id, created_by, created_at, deleted_at FROM task_pre_annotation
    ''')
    
    op.drop_table('task_pre_annotation')
    
    for pre_item in task_pre_annotations:
        attachment = attachments_dict.get(pre_item.file_id)
        
        if not attachment or not attachment.path or not attachment.path.endswith(".jsonl"):
            continue
        
        session.execute(
            sa.text('UPDATE task_pre_annotation_file SET filename=:filename WHERE id=:id'),
            {'filename': attachment.filename, 'id': pre_item.id}
        )
        
    session.commit()
def downgrade() -> None:
    pass
