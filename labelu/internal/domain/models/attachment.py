from datetime import datetime

from sqlalchemy.schema import Index
from sqlalchemy import Column, DateTime, ForeignKey, Integer, SmallInteger, String

from labelu.internal.common.db import Base


class TaskAttachment(Base):
    __tablename__ = "task_attachment"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    path = Column(String(256), comment="file storage path")
    task_id = Column(Integer, ForeignKey("task.id"), index=True)
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    updated_by = Column(Integer, ForeignKey("user.id"), index=True)
    created_at = Column(
        DateTime, default=datetime.now, comment="Time a task was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="Last time a task was updated",
    )
    deleted_at = Column(DateTime, index=True, comment="Task delete time")

    Index("idx_attachment_id_deleted_at", id, deleted_at)
