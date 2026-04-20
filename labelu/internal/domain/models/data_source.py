from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.schema import Index

from labelu.internal.common.db import Base


class DataSource(Base):
    __tablename__ = "data_source"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(128), nullable=False, comment="Display name")
    type = Column(String(32), nullable=False, default="S3", comment="Source type: S3")
    endpoint = Column(String(512), comment="S3 endpoint URL")
    region = Column(String(64), comment="AWS region")
    bucket = Column(String(256), nullable=False, comment="Bucket name")
    prefix = Column(String(512), default="", comment="Default key prefix")
    access_key_id = Column(String(512), comment="Encrypted access key")
    secret_access_key = Column(String(1024), comment="Encrypted secret key")
    path_style = Column(Boolean, default=False, comment="Use path-style addressing")
    use_ssl = Column(Boolean, default=True, comment="Use HTTPS")
    presign_expire_secs = Column(Integer, default=3600, comment="Presigned URL TTL")
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    updated_by = Column(Integer, ForeignKey("user.id"), index=True)
    created_at = Column(
        DateTime(timezone=True), default=datetime.now, comment="Created time"
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
        comment="Updated time",
    )
    deleted_at = Column(DateTime, index=True, comment="Soft delete time")

    Index("idx_datasource_id_deleted_at", id, deleted_at)
