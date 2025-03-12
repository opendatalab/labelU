from datetime import datetime
from typing import Any, Dict, List, Union, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi.encoders import jsonable_encoder

from labelu.internal.domain.models.pre_annotation import TaskPreAnnotation


def batch(db: Session, pre_annotations: List[TaskPreAnnotation]) -> List[TaskPreAnnotation]:
    db.bulk_save_objects(pre_annotations, return_defaults=True)
    return pre_annotations


def list_by(
    db: Session,
    task_id: int | None = None,
    sample_name: str | None = None,
    after: int | None = None,
    before: int | None = None,
    page: int | None = None,
    sorting: str | None = None,
    size: int | None = 10,
) -> Tuple[List[TaskPreAnnotation], int]:

    # query filter
    query_filter = [TaskPreAnnotation.deleted_at == None]
    if before:
        query_filter.append(TaskPreAnnotation.id < before)
    if after:
        query_filter.append(TaskPreAnnotation.id > after)
    if task_id:
        query_filter.append(TaskPreAnnotation.task_id == task_id)
        
    if sample_name:
        query_filter.append(or_(TaskPreAnnotation.sample_name == sample_name, TaskPreAnnotation.sample_name == sample_name[9:]))
        
    query = db.query(TaskPreAnnotation).filter(*query_filter)

    # default order by id, before need select last items
    if before:
        query = query.order_by(TaskPreAnnotation.id.desc())
    else:
        query = query.order_by(TaskPreAnnotation.id.asc())
    
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

def list_by_task_id_and_owner_id(db: Session, task_id: int) -> Dict[str, List[TaskPreAnnotation]]:
    pre_annotations = db.query(TaskPreAnnotation).filter(
        TaskPreAnnotation.task_id == task_id,
        TaskPreAnnotation.deleted_at == None,
    ).all()
    
    return pre_annotations

def list_by_task_id_and_file_id(db: Session, task_id: int, file_id: int) -> List[TaskPreAnnotation]:
    return db.query(TaskPreAnnotation).filter(
        TaskPreAnnotation.task_id == task_id,
        TaskPreAnnotation.deleted_at == None,
        TaskPreAnnotation.file_id == file_id
    ).all()

def list_by_task_id_and_owner_id_and_sample_name(db: Session, task_id: int, sample_name: str) -> List[TaskPreAnnotation]:
    """list pre annotations by task_id, owner_id and sample_name without pagination

    Args:
        db (Session): _description_
        task_id (int): _description_
        owner_id (int): _description_
        sample_name (str): _description_

    Returns:
        List[TaskPreAnnotation]: _description_
    """
    return db.query(TaskPreAnnotation).filter(
        TaskPreAnnotation.task_id == task_id,
        TaskPreAnnotation.deleted_at == None,
        TaskPreAnnotation.sample_name == sample_name
    ).all()

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


def count(db: Session, task_id: int, sample_name: str | None) -> int:
    query_filter = [TaskPreAnnotation.deleted_at == None]
    if task_id:
        query_filter.append(TaskPreAnnotation.task_id == task_id)
        
    if sample_name:
        query_filter.append(TaskPreAnnotation.sample_name == sample_name)
        
    return db.query(TaskPreAnnotation).filter(*query_filter).count()
