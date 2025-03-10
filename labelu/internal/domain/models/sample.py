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
    inner_id = Column(Integer, comment="sample id in a task")
    task_id = Column(Integer, ForeignKey("task.id"), index=True)
    file_id = Column(Integer, ForeignKey("task_attachment.id"), index=True)
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(
        DateTime(timezone=True), default=datetime.now, comment="Time a task sample result was created"
    )
    updated_at = Column(
        DateTime(timezone=True),
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
    deleted_at = Column(DateTime(timezone=True), index=True, comment="Task delete time")

    # 由旧的data里的fileNames和urls中的唯一一个，迁移到media中
    file = relationship("TaskAttachment", foreign_keys=[file_id])
    task = relationship("Task", foreign_keys=[task_id])
    owner = relationship("User", foreign_keys=[created_by])
    updaters = relationship("User", secondary="task_sample_updater")

    Index("idx_sample_id_deleted_at", id, deleted_at)
