from typing import Union

from pydantic import BaseModel, Field


class AutoLabelCommand(BaseModel):
    overwrite: bool = Field(default=True, description="overwrite latest ai-generated pre-annotation")
    template_id: Union[int, None] = Field(default=None, description="reserved prompt template id")
    prompt: Union[str, None] = Field(default=None, description="optional prompt override")
    filter_by_labels: bool = Field(default=True, description="only keep results matching configured labels")


class BatchAutoLabelCommand(BaseModel):
    filter_by_labels: bool = Field(default=True, description="only keep results matching configured labels")
