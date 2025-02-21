from datetime import datetime
from sqlalchemy.schema import Index
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from labelu.internal.common.db import Base

class TaskCollaborator(Base):
    __tablename__ = "task_collaborator"
    
    task_id = Column(
        Integer, 
        ForeignKey("task.id", ondelete="CASCADE"), 
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
        comment="Time a task collaborator was created"
    )
