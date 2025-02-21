from datetime import datetime
from sqlalchemy import or_, exists
from typing import Any, Dict, List, Tuple

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from labelu.internal.domain.models.task import Task
from labelu.internal.domain.models.task_collaborator import TaskCollaborator


def create(db: Session, task: Task) -> Task:
    db.add(task)
    db.flush()
    db.refresh(task)
    return task


def list_by(db: Session, owner_id: int, page: int = 0, size: int = 100) -> Tuple[List[Task], int]:
    collaborator_exists = exists().where(
        TaskCollaborator.task_id == Task.id,
        TaskCollaborator.user_id == owner_id
    )
    query = (
        db.query(Task)
        .filter(
            Task.deleted_at == None,
            or_(
                Task.created_by == owner_id,
                collaborator_exists
            )
        )
    )
    total = query.count()
    
    return (
        query
        .order_by(Task.id.desc())
        .offset(offset=page * size)
        .limit(limit=size)
        .all()
    ), total


def get(db: Session, task_id: int, lock: bool = False) -> Task:
    """return a Task item according to task id

    Args:
        db (Session): a session connect to table
        task_id (int): a given task id
        lock (bool, optional): if lock is True, means add exclusive lock in a row. Defaults to False.
    """
    if not lock:
        return (
            db.query(Task).filter(Task.id == task_id, Task.deleted_at == None).first()
        )
    else:
        return (
            db.query(Task)
            .filter(Task.id == task_id, Task.deleted_at == None)
            .with_for_update()
            .first()
        )


def update(db: Session, db_obj: Task, obj_in: Dict[str, Any]) -> Task:
    obj_data = jsonable_encoder(obj_in)
    for field in obj_data:
        if field in obj_in:
            setattr(db_obj, field, obj_in[field])
    db.add(db_obj)
    db.flush()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, db_obj: Task) -> Task:
    db_obj.deleted_at = datetime.now()
    db.add(db_obj)
    db.flush()
    db.refresh(db_obj)
    return db_obj


def count(db: Session, owner_id: int) -> int:
    return (
        db.query(Task)
        .filter(Task.created_by == owner_id, Task.deleted_at == None)
        .count()
    )
