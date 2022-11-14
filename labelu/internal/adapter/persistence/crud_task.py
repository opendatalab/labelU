from sqlalchemy.orm import Session
from labelu.internal.domain.models.task import Task
from labelu.internal.domain.models.task import TaskFile


def create(db: Session, task: Task) -> Task:
    db_task = Task(
        user_id=task.user_id,
        updated_by=task.user_id,
        name=task.name,
        description=task.description,
        tips=task.tips,
        config=task.config,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def add_file(db: Session, task_file: TaskFile) -> TaskFile:
    db.add(task_file)
    db.commit()
    db.refresh(task_file)
    return task_file
