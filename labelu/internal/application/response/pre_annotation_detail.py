from typing import Union
from pydantic import BaseModel, Field


class PreAnnotationDetailResponse(BaseModel):
    id: Union[int, None] = Field(default=None, description="description: annotation id")
    task_id: Union[int, None] = Field(default=None, description="description: task id")
    pre_annotation_id: Union[int, None] = Field(
        default=None, description="description: pre_annotation id"
    )
    sample_name: Union[str, None] = Field(
        default=None, description="description: sample name"
    )
    data: Union[str, None] = Field(
        default=None, description="description: annotation and config details"
    )
