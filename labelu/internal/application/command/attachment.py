from typing import Annotated, List
from pydantic import BaseModel, Field
from fastapi import UploadFile, File

class AttachmentCommand(BaseModel):
    file: UploadFile = File()


class AttachmentDeleteCommand(BaseModel):
    attachment_ids: List[Annotated[int, Field(gt=0)]] = Field(
        min_length=1,
        description="description: attachment file id",
    )
