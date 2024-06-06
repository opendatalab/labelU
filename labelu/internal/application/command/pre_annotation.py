from typing import List
from pydantic import BaseModel, Field


class CreatePreAnnotationCommand(BaseModel):
    filename: str = Field(
        min_length=1,
        max_length=255,
        description="description: pre annotation filename",
    )
    data: str = Field(
        min_length=1,
        description="description: pre annotation result",
    )

class DeletePreAnnotationCommand(BaseModel):
    pre_annotation_ids: List[int] = Field(
        min_items=1,
        description="description: pre annotation ids",
    )