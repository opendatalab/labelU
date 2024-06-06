from labelu.internal.common.db import Base

from sqlalchemy.schema import Index
from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

class TaskPreAnnotationDetail(Base):
    __tablename__ = "task_pre_annotation_detail"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), index=True)
    pre_annotation_id = Column(Integer, ForeignKey("task_pre_annotation_file.id"), index=True)
    sample_name = Column(String(255), index=True, comment="task sample name")
    created_at = Column(DateTime, index=True, comment="Time a task sample result was created")
    data = Column(Text, comment="task sample pre annotation result")
    deleted_at = Column(DateTime, index=True, comment="Detail delete time")
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    
    pre_annotation = relationship("TaskPreAnnotation", back_populates="details")
    
    Index("idx_pre_annotation_detail_id", id)
    Index("idx_pre_annotation_detail_sample_name", sample_name)
    Index("idx_pre_annotation_detail_task_id_sample_name", task_id, sample_name)