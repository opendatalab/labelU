from datetime import datetime

from typing import Union
from pydantic import BaseModel, EmailStr, Field


class TaskResponse(BaseModel):
    id: Union[int, None] = Field(default=None, description="description: task id")
    name: Union[str, None] = Field(default=None, description="description: task name")
    description: Union[str, None] = Field(
        default=None, description="description: task description"
    )
    tips: Union[str, None] = Field(default=None, description="description: task tips")
    config: Union[str, None] = Field(
        default=None, description="description: task config content"
    )
    media_type: Union[str, None] = Field(
        default=None, description="description: task media type: IMAGE, VIDEO"
    )
    status: Union[str, None] = Field(
        default=None,
        description="description: task status: DRAFT, INPROGRESS, FINISHED",
    )
    created_at: Union[datetime, None] = Field(
        default=0, description="description: task created at time"
    )


class TaskResponseWithProgress(TaskResponse):
    annotated_count: Union[int, None] = Field(
        default=0, description="description: task file already labeled"
    )
    total: Union[int, None] = Field(
        default=0, description="description: task files count"
    )


class UploadResponse(BaseModel):
    id: Union[int, None] = Field(
        default=None, description="description: upload file id"
    )
    filename: Union[str, None] = Field(
        default=None, description="description: upload file name"
    )


class User(BaseModel):
    id: Union[int, None] = None
    username: Union[EmailStr, None] = None


class TaskFileResponse(BaseModel):
    id: int
    path: str = Field(default="", description="description: task status")
    task_id: int = Field(default=0, description="description: task id")
    annotated: int = Field(
        default=0,
        description="description: 0 is has not start yet, 1 is completed, 2 is skipped",
    )
    result: Union[str, None] = Field(
        default=None, description="description: task file annnotation result"
    )
    annotated_by: Union[User, None] = None
    annotated_at: Union[datetime, None] = Field(
        default=None, description="description: task file annnotated time"
    )
