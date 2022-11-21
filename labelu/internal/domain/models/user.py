from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from labelu.internal.common.db import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(
        DateTime, default=datetime.utcnow, comment="Time a task was created"
    )
    updated_at = Column(
        DateTime, default=datetime.utcnow, comment="Last time a task was updated"
    )
