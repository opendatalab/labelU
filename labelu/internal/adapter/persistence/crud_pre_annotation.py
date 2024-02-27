from datetime import datetime
import json
from typing import Any, Dict, List, Union


from sqlalchemy import case, text
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from labelu.internal.domain.models.pre_annotation import TaskPreAnnotation
from labelu.internal.adapter.persistence import crud_attachment


def batch(db: Session, pre_annotations: List[TaskPreAnnotation]) -> List[TaskPreAnnotation]:
    db.bulk_save_objects(pre_annotations, return_defaults=True)
    return pre_annotations


def list_by(
    db: Session,
    task_id: Union[int, None],
    owner_id: int,
    after: Union[int, None],
    before: Union[int, None],
    pageNo: Union[int, None],
    pageSize: int,
    sorting: Union[str, None],
) -> List[TaskPreAnnotation]:

    # query filter
    query_filter = [TaskPreAnnotation.created_by == owner_id, TaskPreAnnotation.deleted_at == None]
    if before:
        query_filter.append(TaskPreAnnotation.id < before)
    if after:
        query_filter.append(TaskPreAnnotation.id > after)
    if task_id:
        query_filter.append(TaskPreAnnotation.task_id == task_id)
    query = db.query(TaskPreAnnotation).filter(*query_filter)

    # default order by id, before need select last items
    if before:
        query = query.order_by(TaskPreAnnotation.id.desc())
    else:
        query = query.order_by(TaskPreAnnotation.id.asc())
    results = (
        query.offset(offset=pageNo * pageSize if pageNo else 0)
        .limit(limit=pageSize)
        .all()
    )
    
    # No sorting
    
    if before:
        results.reverse()
        
    return results

def list_by_task_id_and_owner_id(db: Session, task_id: int, owner_id: int) -> Dict[str, List[TaskPreAnnotation]]:
    pre_annotations = db.query(TaskPreAnnotation).filter(
        TaskPreAnnotation.task_id == task_id,
        TaskPreAnnotation.deleted_at == None,
        TaskPreAnnotation.created_by == owner_id
    ).all()
    
    return pre_annotations

def get(db: Session, pre_annotation_id: int) -> TaskPreAnnotation:
    return (
        db.query(TaskPreAnnotation)
        .filter(TaskPreAnnotation.id == pre_annotation_id, TaskPreAnnotation.deleted_at == None)
        .first()
    )


def get_by_ids(db: Session, pre_annotation_ids: List[int]) -> List[TaskPreAnnotation]:
    return (
        db.query(TaskPreAnnotation)
        .filter(TaskPreAnnotation.id.in_(pre_annotation_ids), TaskPreAnnotation.deleted_at == None)
        .all()
    )


def update(db: Session, db_obj: TaskPreAnnotation, obj_in: Dict[str, Any]) -> TaskPreAnnotation:
    obj_data = jsonable_encoder(obj_in)
    for field in obj_data:
        if field in obj_in:
            setattr(db_obj, field, obj_in[field])
    db.add(db_obj)
    db.flush()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, pre_annotation_ids: List[int]) -> None:
    db.query(TaskPreAnnotation).filter(TaskPreAnnotation.id.in_(pre_annotation_ids)).update(
        {TaskPreAnnotation.deleted_at: datetime.now()}
    )


def count(db: Session, task_id: int, owner_id: int) -> int:
    query_filter = [TaskPreAnnotation.created_by == owner_id, TaskPreAnnotation.deleted_at == None]
    if task_id:
        query_filter.append(TaskPreAnnotation.task_id == task_id)
    return db.query(TaskPreAnnotation).filter(*query_filter).count()
