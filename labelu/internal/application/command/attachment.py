from typing import List, Union
from pydantic import BaseModel, Field
from fastapi import UploadFile, File

from labelu.internal.domain.models.task import MediaType


class AttachmentCommand(BaseModel):
    file: UploadFile = File()


class AttachmentDeleteCommand(BaseModel):
    attachment_ids: List[int] = Field(
        min_items=1,
        gt=0,
        description="description: attachment file id",
    )
