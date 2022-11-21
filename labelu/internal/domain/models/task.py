from enum import Enum
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, SmallInteger, String, Text

from labelu.internal.common.db import Base


class TaskStatus(str, Enum):
    """
    task status
    """

    DRAFT = "DRAFT"
    CONFIGURED = "CONFIGURED"
    INPROGRESS = "INPROGRESS"
    FINISHED = "FINISHED"


class MediaType(str, Enum):
    """
    task meida type
    """

    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(64), index=True)
    description = Column(String(1024), comment="task description")
    tips = Column(String(1024), comment="task tips")
    config = Column(Text, comment="task config yaml")
    media_type = Column(
        String(32),
        comment="task media type: image, video",
    )
    status = Column(String(32), default=TaskStatus.DRAFT.value, comment="task status")
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    updated_by = Column(
        Integer, ForeignKey("user.id"), comment="Last time a task was updated"
    )
    created_at = Column(
        DateTime, default=datetime.utcnow, comment="Time a task was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Last time a task was updated",
    )


class TaskFile(Base):
    __tablename__ = "task_file"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    path = Column(String(256), comment="task status")
    task_id = Column(Integer, ForeignKey("task.id"), index=True)
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    updated_by = Column(Integer, ForeignKey("user.id"), index=True)
    created_at = Column(
        DateTime, default=datetime.utcnow, comment="Time a task was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Last time a task was updated",
    )
    annotated = Column(
        SmallInteger,
        default=0,
        comment="0 is has not start yet, 1 is completed, 2 is skipped",
    )
    result = Column(Text, comment="task file annnotation result")
