from datetime import datetime
from sqlalchemy.schema import Index
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from labelu.internal.common.db import Base

class TaskSampleUpdater(Base):
    __tablename__ = "task_sample_updater"
    
    sample_id = Column(
        Integer, 
        ForeignKey("task_sample.id", ondelete="CASCADE"), 
        primary_key=True,
        index=True
    )
    user_id = Column(
        Integer, 
        ForeignKey("user.id", ondelete="CASCADE"), 
        primary_key=True,
        index=True
    )
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
        comment="created time"
    )
