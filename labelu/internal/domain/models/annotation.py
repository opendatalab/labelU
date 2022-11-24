from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, SmallInteger, Text

from labelu.internal.common.db import Base


class TaskAnnotation(Base):
    __tablename__ = "task_annotation"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), index=True)
    task_file_id = Column(Integer, ForeignKey("task_file.id"), index=True)
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(
        DateTime, default=datetime.now, comment="Time a task was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="Last time a task was updated",
    )
    result_count = Column(
        Integer,
        default=0,
        comment="task file annnotation result count",
    )
    result = Column(Text, comment="task file annnotation result")

    task = relationship("Task", foreign_keys=[task_id])
    task_file = relationship("TaskFile", foreign_keys=[task_file_id])
    owner = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
