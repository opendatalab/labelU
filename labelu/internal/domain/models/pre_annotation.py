from datetime import datetime

from sqlalchemy.schema import Index
from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from labelu.internal.common.db import Base


class TaskPreAnnotation(Base):
    __tablename__ = "task_pre_annotation"
    """Task pre-annotations for a sample of a task.
    """

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), index=True, comment="Task ID")
    sample_name = Column(String(255), index=True, comment="One of the sample names of the task")
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
        comment="Last time a task pre annotation result was updated",
    )
    data = Column(Text, comment="task sample pre annotation result")
    deleted_at = Column(DateTime(timezone=True), index=True, comment="Task pre-annotation delete time")

    file = relationship("TaskAttachment", foreign_keys=[file_id])
    task = relationship("Task", foreign_keys=[task_id])
    owner = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])

    Index("idx_pre_annotation_sample_name", sample_name)
    Index("idx_pre_annotation_id_deleted_at", id, deleted_at)

