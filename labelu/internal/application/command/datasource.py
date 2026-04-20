from typing import Union

from pydantic import BaseModel, Field, model_validator


class CreateDataSourceCommand(BaseModel):
    name: str = Field(max_length=128, description="Display name")
    type: str = Field(default="S3", max_length=32)
    endpoint: Union[str, None] = Field(default=None, max_length=512)
    region: Union[str, None] = Field(default=None, max_length=64)
    bucket: str = Field(max_length=256)
    prefix: str = Field(default="", max_length=512)
    access_key_id: str = Field(max_length=256)
    secret_access_key: str = Field(max_length=256)
    path_style: bool = Field(default=False)
    use_ssl: bool = Field(default=True)
    presign_expire_secs: int = Field(default=3600, ge=60, le=86400)


class UpdateDataSourceCommand(BaseModel):
    name: Union[str, None] = Field(default=None, max_length=128)
    endpoint: Union[str, None] = Field(default=None, max_length=512)
    region: Union[str, None] = Field(default=None, max_length=64)
    bucket: Union[str, None] = Field(default=None, max_length=256)
    prefix: Union[str, None] = Field(default=None, max_length=512)
    access_key_id: Union[str, None] = Field(default=None, max_length=256)
    secret_access_key: Union[str, None] = Field(default=None, max_length=256)
    path_style: Union[bool, None] = None
    use_ssl: Union[bool, None] = None
    presign_expire_secs: Union[int, None] = Field(default=None, ge=60, le=86400)


class ImportS3SamplesCommand(BaseModel):
    data_source_id: int = Field(gt=0)
    object_keys: list[str] = Field(default_factory=list, max_length=10000)
    prefix: Union[str, None] = Field(default=None, max_length=512)
    extension: Union[str, None] = Field(default=None, max_length=256)

    @model_validator(mode='after')
    def check_keys_or_prefix(self):
        if not self.object_keys and self.prefix is None:
            raise ValueError("Either object_keys or prefix must be provided")
        return self
