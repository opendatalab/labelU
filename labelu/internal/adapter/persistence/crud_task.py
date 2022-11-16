from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session
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


def count(db: Session, owner_id: int) -> List[Task]:
    return db.query(Task).filter(Task.user_id == owner_id).count()


def add_file(db: Session, task_file: TaskFile) -> TaskFile:
    db.add(task_file)
    db.commit()
    db.refresh(task_file)
    return task_file


def count_group_by_task(
    db: Session,
    owner_id: int,
    annotated_status: List[int] = None,
) -> dict:
    query_filter = [TaskFile.user_id == owner_id]
    if annotated_status:
        query_filter.append(TaskFile.annotated in annotated_status)

    task_file_count = (
        db.query(TaskFile.task_id, func.count(TaskFile.task_id).label("count"))
        .filter(*query_filter)
        .group_by(TaskFile.task_id)
        .all()
    )
    return dict(task_file_count)
