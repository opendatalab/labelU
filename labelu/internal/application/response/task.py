from typing import Optional
from pydantic import BaseModel, Field


class TaskResponse(BaseModel):
    id: Optional[int] = Field(default=None, description="description: task id")
    name: Optional[str] = Field(default=None, description="description: task name")
    description: Optional[str] = Field(
        default=None, description="description: task description"
    )
    tips: Optional[str] = Field(default=None, description="description: task tips")
    config: Optional[str] = Field(
        default=None, description="description: task config content"
    )
    media_type: Optional[str] = Field(
        default="", description="description: task media type: IMAGE, VIDEO"
    )
    annotated_count: Optional[int] = Field(
        default=0, description="description: task file already labeled"
    )
    total: Optional[int] = Field(default=0, description="description: task files count")


class UploadResponse(BaseModel):
    filename: Optional[str]
