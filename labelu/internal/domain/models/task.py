from enum import Enum
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import relationship

from labelu.internal.common.db import Base


class TaskStatus(Enum):
    """
    business error code
    """

    DRAFT = "DRAFT"
    INPROGRESS = "INPROGRESS"
    FINISHED = "DRAFT"


class TaskDataType(Enum):
    """
    business error code
    """

    IMAGE = "IMAGE"


class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    status = Column(String(32), default=TaskStatus.DRAFT.value, comment="task status")
    name = Column(String(64), index=True)
    description = Column(String(1024), comment="task description")
    tips = Column(String(1024), comment="task tips")
    config = Column(Text, comment="task config yaml")
    data_type = Column(Text, comment="task config yaml")
    created_at = Column(
        DateTime, default=datetime.utcnow(), comment="Time a task was created"
    )
    updated_at = Column(
        DateTime, default=datetime.utcnow(), comment="Last time a task was updated"
    )
    updated_by = Column(Integer, index=True)


class TaskFile(Base):
    __tablename__ = "task_file"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(32), default=TaskStatus.DRAFT.value, comment="task status")
    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    task_id = Column(Integer, ForeignKey("task.id"), index=True)
    created_at = Column(
        DateTime, default=datetime.utcnow(), comment="Time a task was created"
    )
    updated_at = Column(
        DateTime, default=datetime.utcnow(), comment="Last time a task was updated"
    )
    updated_by = Column(Integer, ForeignKey("user.id"), index=True)
    is_labeled = Column(
        SmallInteger,
        default=0,
        comment="0 is has not start yet, 1 is completed, 2 is skipped",
    )
    result = Column(Text, comment="task file annnotation result")