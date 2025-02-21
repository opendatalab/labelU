from enum import Enum
from datetime import datetime

from sqlalchemy.schema import Index
from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from labelu.internal.common.db import Base


class TaskStatus(str, Enum):
    """
    task status
    """

    DRAFT = "DRAFT"
    IMPORTED = "IMPORTED"
    CONFIGURED = "CONFIGURED"
    INPROGRESS = "INPROGRESS"
    FINISHED = "FINISHED"


class MediaType(str, Enum):
    """
    task meida type
    """

    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"


class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(64), index=True)
    description = Column(String(1024), comment="task description")
    tips = Column(String(1024), comment="task tips")
    last_sample_inner_id = Column(
        Integer, default=0, comment="The last inner id of sample in a task"
    )
    config = Column(Text, comment="task config yaml")
    media_type = Column(
        String(32),
        comment="task media type: image, video, audio",
    )
    status = Column(String(32), default=TaskStatus.DRAFT.value, comment="task status")
    created_by = Column(Integer, ForeignKey(column="user.id"), index=True)
    updated_by = Column(
        Integer, ForeignKey(column="user.id"), comment="Last time a task was updated by"
    )
    created_at = Column(
        DateTime(timezone=True), default=datetime.now, comment="Time a task was created"
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
        comment="Last time a task was updated",
    )
    deleted_at = Column(DateTime(timezone=True), index=True, comment="Task delete time")
    
    collaborators = relationship("User", secondary="task_collaborator", back_populates="tasks")
    owner = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])

    Index("idx_task_id_deleted_at_index", id, deleted_at)
