from typing import List
from pydantic import BaseModel, Field


class CreatePreAnnotationCommand(BaseModel):
    file_id: int = Field(
        gt=0,
        description="description: attachment file id",
    )

class DeletePreAnnotationCommand(BaseModel):
    pre_annotation_ids: List[int] = Field(
        min_items=1,
        description="description: pre annotation ids",
    )