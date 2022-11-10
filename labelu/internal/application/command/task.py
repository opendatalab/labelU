from typing import Optional
from pydantic import BaseModel, Field
from fastapi import UploadFile, File


class BasicConfigCommand(BaseModel):
    name: str = Field(description="description: task name", max_length=50)
    description: str = Field(
        default=None, description="description: task description", max_length=1000
    )
    tips: Optional[str] = Field(
        default=None, description="description: task tips", max_length=500
    )


class UploadCommand(BaseModel):
    file: UploadFile = File()


class UpdateCommand(BaseModel):
    name: Optional[str] = Field(
        default=None, description="description: task name", max_length=50
    )
    description: Optional[str] = Field(
        default=None, description="description: task description", max_length=1000
    )
    tips: Optional[str] = Field(
        default=None, description="description: task tips", max_length=500
    )
    config: Optional[str] = Field(
        default=None, description="description: task config content"
    )
