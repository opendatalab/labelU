from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from labelu.internal.common.db import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    created_at = Column(
        DateTime(timezone=True), default=datetime.now, comment="Time a task was created"
    )
    updated_at = Column(
        DateTime(timezone=True), default=datetime.now, comment="Last time a task was updated"
    )
    tasks = relationship("Task", secondary="task_collaborator", back_populates="collaborators")
