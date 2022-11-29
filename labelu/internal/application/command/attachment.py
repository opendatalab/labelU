from typing import List, Union
from pydantic import BaseModel, Field
from fastapi import UploadFile, File

from labelu.internal.domain.models.task import MediaType


class AttachmentCommand(BaseModel):
    file: UploadFile = File()
    path: Union[str, None] = Field(default="", description="description: file path")


class AttachmentDeleteCommand(BaseModel):
    attachment_ids: List[int] = Field(
        min_items=1,
        description="description: attachment file id",
    )
