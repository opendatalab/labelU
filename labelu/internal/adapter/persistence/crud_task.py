from typing import Any, Dict, List, Optional, Union

from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from labelu.internal.domain.models.task import Task
from labelu.internal.domain.models.task import TaskFile


def create(db: Session, task: Task) -> Task:
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list(db: Session, owner_id: int, page: int = 0, size: int = 100) -> List[Task]:
    return (
        db.query(Task)
        .filter(Task.user_id == owner_id)
        .offset(offset=page * size)
        .limit(limit=size)
        .all()
    )


def get(db: Session, id: str) -> Task:
    return db.query(Task).filter(Task.id == id).first()


def update(db: Session, db_obj: Task, obj_in: Dict[str, Any]) -> Task:
    obj_data = jsonable_encoder(obj_in)
    for field in obj_data:
        if field in obj_in:
            setattr(db_obj, field, obj_in[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def add_file(db: Session, task_file: TaskFile) -> TaskFile:
    db.add(task_file)
    db.commit()
    db.refresh(task_file)
    return task_file


def list_upload_files(
    db: Session, task_id: int, owner_id: int, page: int = 0, size: int = 100
) -> List[TaskFile]:
    return (
        db.query(TaskFile)
        .filter(TaskFile.created_by == owner_id, TaskFile.task_id == task_id)
        .offset(offset=page * size)
        .limit(limit=size)
        .all()
    )


def count(db: Session, owner_id: int) -> List[Task]:
    return db.query(Task).filter(Task.user_id == owner_id).count()


def count_task_file(db: Session, task_id: int, owner_id: int) -> List[Task]:
    return (
        db.query(TaskFile)
        .filter(TaskFile.created_by == owner_id, TaskFile.task_id == task_id)
        .count()
    )


def count_task_file_group_by_task(
    db: Session,
    owner_id: int,
    task_id: int = None,
    annotated_status: List[int] = None,
) -> dict:
    query_filter = [TaskFile.created_by == owner_id]
    if annotated_status:
        query_filter.append(TaskFile.annotated in annotated_status)
    if task_id:
        query_filter.append(TaskFile.task_id == task_id)

    task_file_count = (
        db.query(TaskFile.task_id, func.count(TaskFile.task_id).label("count"))
        .filter(*query_filter)
        .group_by(TaskFile.task_id)
        .all()
    )
    return dict(task_file_count)
