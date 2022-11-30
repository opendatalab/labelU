from typing import Any, Dict, List, Union


from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from labelu.internal.domain.models.sample import TaskSample


def batch(db: Session, samples: List[TaskSample]) -> List[TaskSample]:
    db.bulk_save_objects(samples, return_defaults=True)
    db.commit()
    return samples


def list_by(
    db: Session,
    owner_id: int,
    after: Union[int, None],
    before: Union[int, None],
    pageNo: Union[int, None],
    pageSize: int,
) -> List[TaskSample]:
    offset = after
    if pageNo != None:
        offset = pageNo * pageSize
    if before:
        offset = before - pageSize

    query_filter = [TaskSample.created_by == owner_id]
    if before:
        query_filter.append(TaskSample.id < before)

    return (
        db.query(TaskSample)
        .filter(*query_filter)
        .order_by(TaskSample.id.asc())
        .offset(offset=offset)
        .limit(limit=pageSize)
        .all()
    )


def get(db: Session, sample_id: int) -> TaskSample:
    return db.query(TaskSample).filter(TaskSample.id == sample_id).first()


def update(db: Session, db_obj: TaskSample, obj_in: Dict[str, Any]) -> TaskSample:
    obj_data = jsonable_encoder(obj_in)
    for field in obj_data:
        if field in obj_in:
            setattr(db_obj, field, obj_in[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, sample_ids: List[int]) -> None:
    db.query(TaskSample).filter(TaskSample.id.in_(sample_ids)).delete()
    db.commit()


def count(db: Session, owner_id: int) -> int:
    return db.query(TaskSample).filter(TaskSample.created_by == owner_id).count()


def statics(
    db: Session,
    owner_id: int,
    task_id: int = None,
) -> dict:
    query_filter = [TaskSample.created_by == owner_id]
    if task_id:
        query_filter.append(TaskSample.task_id == task_id)

    statics = (
        db.query(
            TaskSample.task_id,
            TaskSample.state,
            func.count(TaskSample.state).label("count"),
        )
        .filter(*query_filter)
        .group_by(TaskSample.task_id, TaskSample.state)
        .all()
    )
    d = {f"{s[0]}_{s[1]}": s[2] for s in statics}
    return d
