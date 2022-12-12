from enum import Enum
from datetime import datetime

from sqlalchemy.schema import Index
from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from labelu.internal.common.db import Base


class SampleState(str, Enum):
    """
    task sample state
    """

    NEW = "NEW"
    SKIPPED = "SKIPPED"
    DONE = "DONE"


class TaskSample(Base):
    __tablename__ = "task_sample"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), index=True)
    task_attachment_ids = Column(String(255), comment="task sample attachment ids")
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(
        DateTime, default=datetime.now, comment="Time a task sample result was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="Last time a task sample result was updated",
    )
    annotated_count = Column(
        Integer,
        default=0,
        comment="task sample result count",
    )
    data = Column(Text, comment="task sample result")
    state = Column(
        String(32),
        default=SampleState.NEW.value,
        comment="NEW is has not start yet, DONE is completed, SKIPPED is skipped",
    )
    deleted_at = Column(DateTime, index=True, comment="Task delete time")

    task = relationship("Task", foreign_keys=[task_id])
    owner = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])

    Index("idx_sample_id_deleted_at", id, deleted_at)
