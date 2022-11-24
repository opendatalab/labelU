from datetime import datetime

from typing import List, Union
from pydantic import BaseModel, Field

from labelu.internal.application.response.base import UserResp
from labelu.internal.application.response.task import TaskFileResponse


class TaskAnnotationResponse(BaseModel):
    id: Union[int, None] = Field(default=None, description="description: annotation id")
    results: Union[str, None] = Field(
        default=None, description="description: annotate result list"
    )
    result_count: Union[str, None] = Field(
        default=None, description="description: annotate result count"
    )
    created_at: Union[datetime, None] = Field(
        default=None, description="description: task created at time"
    )
    created_by: Union[UserResp, None] = Field(
        default=None, description="description: task created by"
    )
    updated_at: Union[datetime, None] = Field(
        default=None, description="description: task updated at time"
    )
    updated_by: Union[UserResp, None] = Field(
        default=None, description="description: task updated by"
    )
