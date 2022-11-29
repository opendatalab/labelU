from typing import Union
from pydantic import BaseModel, Field

from labelu.internal.domain.models.task import MediaType


class BasicConfigCommand(BaseModel):
    name: str = Field(description="description: task name", max_length=50)
    description: str = Field(
        default=None, description="description: task description", max_length=500
    )
    tips: Union[str, None] = Field(
        default=None, description="description: task tips", max_length=1000
    )


class UpdateCommand(BaseModel):
    name: Union[str, None] = Field(
        default=None, description="description: task name", max_length=50
    )
    description: Union[str, None] = Field(
        default=None, description="description: task description", max_length=500
    )
    tips: Union[str, None] = Field(
        default=None, description="description: task tips", max_length=1000
    )
    media_type: Union[MediaType, None] = Field(
        default=None, description="description: task config content"
    )
    config: Union[str, None] = Field(
        default=None, description="description: task config content"
    )
