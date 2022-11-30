from datetime import datetime

from typing import Union
from pydantic import BaseModel, EmailStr, Field

from labelu.internal.application.response.base import UserResp


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
        description="description: task status: DRAFT, IMPORTED, CONFIGURED, INPROGRESS, FINISHED",
    )
    created_at: Union[datetime, None] = Field(
        default=None, description="description: task created at time"
    )
    created_by: Union[UserResp, None] = Field(
        default=None, description="description: task created at time"
    )


class TaskStatics(BaseModel):
    new: Union[int, None] = Field(
        default=0, description="description: count for task data have not labeled yet"
    )
    done: Union[int, None] = Field(
        default=0, description="description: count for task data already labeled"
    )
    skipped: Union[int, None] = Field(
        default=0, description="description: count for task data skipped"
    )


class TaskResponseWithStatics(TaskResponse):
    stats: Union[TaskStatics, None] = None


class User(BaseModel):
    id: Union[int, None] = None
    username: Union[EmailStr, None] = None
