from typing import Union
from pydantic import BaseModel, EmailStr, Field


class AttachmentResponse(BaseModel):
    id: Union[int, None] = Field(
        default=None, description="description: upload file id"
    )
    url: Union[str, None] = Field(
        default=None, description="description: upload file url"
    )
    status: Union[bool, None] = Field(
        default=False,
        description="description: upload file status, 0 is upload failure, 1 is upload success",
    )
