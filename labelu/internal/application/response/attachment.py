from typing import Union
from pydantic import BaseModel, Field


class AttachmentResponse(BaseModel):
    id: Union[int, None] = Field(
        default=None, description="description: upload file id"
    )
    url: Union[str, None] = Field(
        default=None, description="description: upload file url"
    )
    thumbnail_url: Union[str, None] = Field(
        default=None, description="description: upload file thumbnail url"
    )
    stream_url: Union[str, None] = Field(
        default=None, description="description: upload file stream url"
    )
    storage_backend: Union[str, None] = Field(
        default=None, description="description: upload file storage backend"
    )
    filename: Union[str, None] = Field(
        default=None, description="description: upload file name"
    )
    
