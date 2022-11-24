from typing import Union
from pydantic import BaseModel, Field


class SubmitResultCommand(BaseModel):
    skipped: Union[bool, None] = Field(
        default=False,
        description="description: annotate skipped, false is not skipped, true is skipped",
    )
    result_count: Union[int, None] = Field(
        default=None, description="description: annotate result count"
    )
    results: Union[str, None] = Field(
        default=None, description="description: annotate result list, is json lists"
    )
