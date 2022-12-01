from typing import Union
from pydantic import BaseModel, Field


class AttachmentResponse(BaseModel):
    id: Union[int, None] = Field(
        default=None, description="description: upload file id"
    )
    url: Union[str, None] = Field(
        default=None, description="description: upload file url"
    )
