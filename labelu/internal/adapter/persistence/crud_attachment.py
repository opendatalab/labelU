from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from labelu.internal.domain.models.attachment import TaskAttachment

def list_by(
    db: Session,
    size: int,
    ids: List[int] | None = [],
    task_id: Optional[int] = None,
    owner_id: Optional[int] = None,
    after: Optional[int] = None,
    before: Optional[int] = None,
    page: Optional[int] = None,
    sorting: Optional[str] = None,
) -> Tuple[List[TaskAttachment], int]:
# query filter
    query_filter = [TaskAttachment.deleted_at == None, TaskAttachment.id.in_(ids)]
    if owner_id:
        query_filter.append(TaskAttachment.created_by == owner_id)
        
    if before:
        query_filter.append(TaskAttachment.id < before)
    if after:
        query_filter.append(TaskAttachment.id > after)
    if task_id:
        query_filter.append(TaskAttachment.task_id == task_id)
        
    query = db.query(TaskAttachment).filter(*query_filter)

    # default order by id, before need select last items
    if before:
        query = query.order_by(TaskAttachment.id.desc())
    else:
        query = query.order_by(TaskAttachment.id.asc())
        
    count = query.count()
    
    results = (
        query.offset(offset=page * size if page else 0)
        .limit(limit=size)
        .all()
    )
    
    if sorting:
        field, order = sorting.split(":")
        if order == "desc":
            results = sorted(results, key=lambda x: getattr(x, field), reverse=True)
        else:
            results = sorted(results, key=lambda x: getattr(x, field))
    
    if before:
        results.reverse()
        
    return results, count

def create(db: Session, attachment: TaskAttachment) -> TaskAttachment:
    db.add(attachment)
    db.flush()
    db.refresh(attachment)
    return attachment


def get(db: Session, attachment_id: int) -> TaskAttachment:
    return (
        db.query(TaskAttachment)
        .filter(TaskAttachment.id == attachment_id, TaskAttachment.deleted_at == None)
        .first()
    )


def get_by_ids(db: Session, attachment_ids: List[int]) -> List[TaskAttachment]:
    return (
        db.query(TaskAttachment)
        .filter(
            TaskAttachment.id.in_(attachment_ids), TaskAttachment.deleted_at == None
        )
        .all()
    )


def delete(db: Session, attachment_ids: List[int]) -> None:
    db.query(TaskAttachment).filter(TaskAttachment.id.in_(attachment_ids)).update(
        {TaskAttachment.deleted_at: datetime.now()}
    )
