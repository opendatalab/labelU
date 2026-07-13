from enum import Enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from labelu.internal.common.db import Base


class ExportStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ExportJob(Base):
    __tablename__ = "export_job"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), index=True)
    created_by = Column(Integer, ForeignKey("user.id"))
    export_type = Column(String(32))
    status = Column(String(32), default=ExportStatus.PENDING.value)
    sample_count = Column(Integer, default=0)
    processed_count = Column(Integer, default=0)
    file_path = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    sample_ids = Column(Text)  # JSON string of ids
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
