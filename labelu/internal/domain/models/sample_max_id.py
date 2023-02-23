from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer

from labelu.internal.common.db import Base


class TaskSampleMaxId(Base):
    __tablename__ = 'task_sample_max_id'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), index=True)
    sample_max_id = Column(Integer, default=0, comment="The max sample id of task")
    create_by = Column(Integer, ForeignKey("user.id"), index=True)
    create_at = Column(DateTime, default=datetime.now, comment="The first time to create sample of a task")
    update_by = Column(Integer, ForeignKey("user.id"))
    update_at = Column(DateTime, default=datetime.now, comment="Last time a sample was updated")

    task = relationship("Task", foreign_keys=[task_id])
    owner = relationship("User", foreign_keys=[create_by])
    updater = relationship("User", foreign_keys=[update_by])
