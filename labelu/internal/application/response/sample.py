from datetime import datetime

from typing import List, Union
from pydantic import BaseModel, Field

from labelu.internal.application.response.base import UserResp


class CreateSampleResponse(BaseModel):
    ids: Union[List[int], None] = Field(
        default=None, description="description: attachment ids"
    )


class SampleResponse(BaseModel):
    id: Union[int, None] = Field(default=None, description="description: annotation id")
    state: Union[str, None] = Field(
        default=None,
        description="description: sample file state, NEW is has not start yet, DONE is completed, SKIPPED is skipped",
    )
    data: Union[dict, None] = Field(
        default=None,
        description="description: sample data, include filename, file url, or result",
    )
    annotated_count: Union[int, None] = Field(
        default=0, description="description: annotate result count"
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
