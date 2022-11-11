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


class UploadResponse(BaseModel):
    files: Optional[str]
