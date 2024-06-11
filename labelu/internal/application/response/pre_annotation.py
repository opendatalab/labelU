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
    details: Union[object, None] = Field(
        default=None, description="description: pre annotation details"
    )
    filename: Union[str, None] = Field(
        default=None, description="description: pre annotation file name"
    )
    created_at: Union[datetime, None] = Field(
        default=None, description="description: created at time"
    )
    created_by: Union[UserResp, None] = Field(
        default=None, description="description: created by"
    )
