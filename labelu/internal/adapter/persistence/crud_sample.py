from datetime import datetime
from typing import Any, Dict, List, Union


from sqlalchemy import case, func, text
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from labelu.internal.domain.models.sample import SampleState
from labelu.internal.domain.models.sample import TaskSample


def batch(db: Session, samples: List[TaskSample]) -> List[TaskSample]:
    db.bulk_save_objects(samples, return_defaults=True)
    return samples


def list_by(
    db: Session,
    task_id: Union[int, None],
    after: Union[int, None],
    before: Union[int, None],
    page: Union[int, None],
    size: int,
    sorting: Union[str, None],
) -> List[TaskSample]:

    # query filter
    query_filter = [TaskSample.deleted_at == None]
    if before:
        query_filter.append(TaskSample.id < before)
    if after:
        query_filter.append(TaskSample.id > after)
    if task_id:
        query_filter.append(TaskSample.task_id == task_id)
    query = db.query(TaskSample).filter(*query_filter)

    # case when for state enum
    whens = {state: index for index, state in enumerate(SampleState)}
    sort_logic = case(value=TaskSample.state, whens=whens).label(TaskSample.state.key)

    if sorting:
        sort_strings = sorting.split(",")
        for item in sort_strings:
            sort_key = item.split(":")
            if sort_key[0] == TaskSample.state.key:
                if sort_key[1] == "asc":
                    query = query.order_by(sort_logic.asc())
                else:
                    query = query.order_by(sort_logic.desc())
            else:
                query = query.order_by(text(f"{sort_key[0]} {sort_key[1]}"))

    # default order by id, before need select last items
    if before:
        query = query.order_by(TaskSample.id.desc())
    else:
        query = query.order_by(TaskSample.id.asc())
    results = (
        query.offset(offset=page * size if page else 0)
        .limit(limit=size)
        .all()
    )
    if before:
        results.reverse()
    return results


def get(db: Session, sample_id: int) -> TaskSample:
    return (
        db.query(TaskSample)
        .filter(TaskSample.id == sample_id, TaskSample.deleted_at == None)
        .first()
    )


def get_by_ids(db: Session, sample_ids: List[int]) -> List[TaskSample]:
    return (
        db.query(TaskSample)
        .filter(TaskSample.id.in_(sample_ids), TaskSample.deleted_at == None)
        .all()
    )


def update(db: Session, db_obj: TaskSample, obj_in: Dict[str, Any]) -> TaskSample:
    obj_data = jsonable_encoder(obj_in)
    for field in obj_data:
        if field in obj_in:
            setattr(db_obj, field, obj_in[field])
    db.add(db_obj)
    db.flush()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, sample_ids: List[int]) -> None:
    db.query(TaskSample).filter(TaskSample.id.in_(sample_ids)).update(
        {TaskSample.deleted_at: datetime.now()}
    )


def count(db: Session, task_id: int) -> int:
    query_filter = [TaskSample.deleted_at == None]
    if task_id:
        query_filter.append(TaskSample.task_id == task_id)
    return db.query(TaskSample).filter(*query_filter).count()


def statics(
    db: Session,
    task_ids: List[int],
) -> dict:
    query_filter = [TaskSample.deleted_at == None]
    if task_ids:
        query_filter.append(TaskSample.task_id.in_(task_ids))

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
