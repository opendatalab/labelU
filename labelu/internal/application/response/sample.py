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
    inner_id: Union[int, None] = Field(default=None, description="description: inner id of a sample in task")
    state: Union[str, None] = Field(
        default=None,
        description="description: sample file state, NEW is has not start yet, DONE is completed, SKIPPED is skipped",
    )
    data: Union[object, None] = Field(
        default=None,
        description="description: sample data, include filename, file url, or result",
    )
    file: Union[object, None] = Field(
        default=None, description="description: media attachment file"
    )
    is_pre_annotated: Union[bool, None] = Field(
        default=False, description="description: is pre annotated"
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
    updaters: List[UserResp] | None = Field(
        default=[], description="description: sample updaters"
    )
