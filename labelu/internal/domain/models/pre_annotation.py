from datetime import datetime

from sqlalchemy.schema import Index
from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from labelu.internal.common.db import Base


class TaskPreAnnotation(Base):
    __tablename__ = "task_pre_annotation_file"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), index=True)
    filename = Column(String(255), comment="task sample pre annotation file name")
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    created_at = Column(
        DateTime, default=datetime.now, comment="Time a task sample result was created"
    )
    deleted_at = Column(DateTime, index=True, comment="Task delete time")
    
    details = relationship("TaskPreAnnotationDetail", back_populates="pre_annotation")
    task = relationship("Task", foreign_keys=[task_id])
    owner = relationship("User", foreign_keys=[created_by])

    Index("idx_pre_annotation_file_id_deleted_at", id, deleted_at)

