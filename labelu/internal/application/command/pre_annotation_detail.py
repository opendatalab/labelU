from pydantic import BaseModel, Field


class DeletePreAnnotationDetailCommand(BaseModel):
    pre_annotation_id: int = Field(
        description="description: pre annotation id",
    )