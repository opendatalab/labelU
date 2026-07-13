import ipaddress
import socket
from typing import Union
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator


def validate_s3_endpoint(endpoint: Union[str, None]) -> Union[str, None]:
    """Reject S3 endpoints that could be abused for SSRF.

    Only http(s) URLs are allowed, and the host must not resolve to a
    loopback/private/link-local/reserved address (e.g. the cloud metadata
    endpoint 169.254.169.254 or internal services).
    """
    if endpoint is None or endpoint == "":
        return endpoint

    parsed = urlparse(endpoint)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("endpoint must be an http(s) URL")
    host = parsed.hostname
    if not host:
        raise ValueError("endpoint must include a host")

    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        raise ValueError("endpoint host cannot be resolved")

    for info in infos:
        addr = ipaddress.ip_address(info[4][0])
        if (
            addr.is_private
            or addr.is_loopback
            or addr.is_link_local
            or addr.is_reserved
            or addr.is_multicast
            or addr.is_unspecified
        ):
            raise ValueError("endpoint host resolves to a disallowed address")
    return endpoint


class CreateDataSourceCommand(BaseModel):
    name: str = Field(max_length=128, description="Display name")
    type: str = Field(default="S3", max_length=32)
    endpoint: Union[str, None] = Field(default=None, max_length=512)

    _validate_endpoint = field_validator("endpoint")(validate_s3_endpoint)
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

    _validate_endpoint = field_validator("endpoint")(validate_s3_endpoint)
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
