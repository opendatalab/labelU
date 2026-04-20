from datetime import datetime

from sqlalchemy.schema import Index
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from labelu.internal.common.db import Base


class TaskAttachment(Base):
    __tablename__ = "task_attachment"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    filename = Column(String(256), comment="file name")
    url = Column(String(256), comment="file url")
    path = Column(String(256), comment="file storage path or S3 object key")
    task_id = Column(Integer, ForeignKey("task.id"), index=True)
    data_source_id = Column(
        Integer, ForeignKey("data_source.id"), nullable=True, index=True,
        comment="NULL = local upload, set = imported from external data source",
    )
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    updated_by = Column(Integer, ForeignKey("user.id"), index=True)
    created_at = Column(
        DateTime(timezone=True), default=datetime.now, comment="Time a task was created"
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
        comment="Last time a task was updated",
    )
    deleted_at = Column(DateTime, index=True, comment="Task delete time")

    data_source = relationship("DataSource", lazy="joined")

    Index("idx_attachment_id_deleted_at", id, deleted_at)
