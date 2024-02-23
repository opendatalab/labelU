from datetime import datetime

from typing import List, Union
from pydantic import BaseModel, Field

from labelu.internal.application.response.base import UserResp


class CreatePreAnnotationResponse(BaseModel):
    ids: Union[List[int], None] = Field(
        default=None, description="description: attachment ids"
    )


class PreAnnotationResponse(BaseModel):
    id: Union[int, None] = Field(default=None, description="description: annotation id")
    file: Union[object, None] = Field(
        default=None, description="description: media attachment file"
    )
    data: Union[object, None] = Field(
        default=None,
        description="description: sample data, include filename, file url, or result",
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
