from typing import Union
from datetime import datetime

from pydantic import BaseModel, Field


class DataSourceResponse(BaseModel):
    id: int
    name: str
    type: str
    endpoint: Union[str, None] = None
    region: Union[str, None] = None
    bucket: str
    prefix: str = ""
    path_style: bool = False
    use_ssl: bool = True
    presign_expire_secs: int = 3600
    created_by: int
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None


class S3ObjectItem(BaseModel):
    key: str
    size: int = 0
    last_modified: Union[str, None] = None


class S3ObjectListResponse(BaseModel):
    objects: list[S3ObjectItem] = []
    next_page_token: Union[str, None] = None
    truncated: bool = False
