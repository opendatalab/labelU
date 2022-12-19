from enum import Enum
from typing import List, Union
from pydantic import BaseModel, Field

from labelu.internal.domain.models.sample import SampleState


class ExportType(str, Enum):
    """
    export samle result file type
    """

    JSON = "JSON"
    MASK = "MASK"
    COCO = "COCO"


class CreateSampleCommand(BaseModel):
    attachement_ids: List[int] = Field(
        min_items=1,
        gt=0,
        description="description: attachment file id",
    )
    data: Union[dict, None] = Field(
        default=None,
        description="description: sample data, include filename, file url, or result",
    )


class DeleteSampleCommand(BaseModel):
    sample_ids: List[int] = Field(
        min_items=1,
        gt=0,
        description="description: attachment file id",
    )


class PatchSampleCommand(BaseModel):
    data: Union[dict, None] = Field(
        default=None,
        description="description: sample data, include filename, file url, or result",
    )
    annotated_count: Union[int, None] = Field(
        default=0, description="description: annotate result count"
    )
    state: Union[SampleState, None] = Field(
        description="description: sample file state, must be 'SKIPPED', 'NEW', or None",
    )


class ExportSampleCommand(BaseModel):
    sample_ids: Union[List[int], None] = Field(
        min_items=1,
        gt=0,
        description="description: sample id",
    )
