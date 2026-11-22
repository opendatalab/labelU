from datetime import datetime
from typing import Any, Dict, List, Union


from sqlalchemy import case, func
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
    whens = {state.value: index for index, state in enumerate(SampleState)}
    sort_logic = case(whens, value=TaskSample.state).label(TaskSample.state.key)

    # Allowlist of sortable columns mapped to real ORM columns. Only these
    # identifiers may reach ORDER BY; anything else is rejected so request
    # input can never be interpolated into raw SQL.
    sortable_columns = {
        "inner_id": TaskSample.inner_id,
        "updated_at": TaskSample.updated_at,
        "annotated_count": TaskSample.annotated_count,
    }

    if sorting:
        sort_strings = sorting.split(",")
        for item in sort_strings:
            sort_key = item.split(":")
            column = sort_key[0]
            direction = sort_key[1] if len(sort_key) > 1 else "asc"
            if direction not in ("asc", "desc"):
                continue
            if column == TaskSample.state.key:
                order_target = sort_logic
            elif column in sortable_columns:
                order_target = sortable_columns[column]
            else:
                continue
            query = query.order_by(
                order_target.asc() if direction == "asc" else order_target.desc()
            )

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


_SQL_IN_CHUNK_SIZE = 500


def get_by_ids(db: Session, sample_ids: List[int], task_id: Union[int, None] = None) -> List[TaskSample]:
    if not sample_ids:
        return []
    unique_ids = list(dict.fromkeys(sample_ids))
    results: List[TaskSample] = []
    for start in range(0, len(unique_ids), _SQL_IN_CHUNK_SIZE):
        chunk = unique_ids[start : start + _SQL_IN_CHUNK_SIZE]
        query_filter = [TaskSample.id.in_(chunk), TaskSample.deleted_at == None]
        if task_id is not None:
            query_filter.append(TaskSample.task_id == task_id)
        results.extend(db.query(TaskSample).filter(*query_filter).all())
    results.sort(key=lambda s: s.id)
    return results


def list_new_samples(db: Session, task_id: int) -> List[TaskSample]:
    return (
        db.query(TaskSample)
        .filter(
            TaskSample.task_id == task_id,
            TaskSample.state == SampleState.NEW.value,
            TaskSample.deleted_at == None,
        )
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
    now = datetime.now()
    for start in range(0, len(sample_ids), _SQL_IN_CHUNK_SIZE):
        chunk = sample_ids[start : start + _SQL_IN_CHUNK_SIZE]
        db.query(TaskSample).filter(TaskSample.id.in_(chunk)).update(
            {TaskSample.deleted_at: now}, synchronize_session=False
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
