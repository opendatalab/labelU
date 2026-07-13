import ipaddress
import socket
from typing import Union
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator

from labelu.internal.common.config import settings


# Networks that are never a valid S3 endpoint and must be blocked regardless of
# ALLOW_PRIVATE_S3_ENDPOINT. 100.64.0.0/10 is RFC6598 shared address space
# (Carrier-Grade NAT) and is NOT flagged private/link-local/reserved by the
# stdlib, yet it hosts the Alibaba/Tencent cloud metadata service
# (100.100.100.200) — so it must be rejected explicitly.
_ALWAYS_BLOCK_NETWORKS = (
    ipaddress.ip_network("100.64.0.0/10"),
)


def validate_s3_endpoint(endpoint: Union[str, None]) -> Union[str, None]:
    """Reject S3 endpoints that could be abused for SSRF.

    Only http(s) URLs are allowed. Link-local (cloud metadata
    169.254.0.0/16, fe80::/10), multicast, reserved, unspecified and RFC6598
    shared-address-space (100.64.0.0/10, incl. Alibaba/Tencent metadata)
    addresses are always rejected — they are never valid S3 endpoints.

    Private (RFC1918 / ULA) and loopback addresses are allowed when
    ``settings.ALLOW_PRIVATE_S3_ENDPOINT`` is true (the default, for on-prem
    deployments backed by an internal MinIO/S3-compatible store) and
    rejected otherwise (strict mode).
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

    allow_private = settings.ALLOW_PRIVATE_S3_ENDPOINT
    for info in infos:
        addr = ipaddress.ip_address(info[4][0])
        # Never a legitimate S3 endpoint; always rejected regardless of config.
        # Note: the metadata IP (169.254.x) is also flagged is_private on newer
        # Python, so link-local is checked here and must win over the private
        # carve-out below. Loopback is exempt from the reserved check because
        # ::1 is also flagged is_reserved.
        in_blocked_net = any(
            addr.version == net.version and addr in net
            for net in _ALWAYS_BLOCK_NETWORKS
        )
        if (
            addr.is_link_local
            or addr.is_multicast
            or addr.is_unspecified
            or (addr.is_reserved and not addr.is_loopback)
            or in_blocked_net
        ):
            raise ValueError("endpoint host resolves to a disallowed address")
        # Internal networks (RFC1918 / ULA / loopback): allowed only when
        # explicitly permitted via ALLOW_PRIVATE_S3_ENDPOINT.
        if (addr.is_private or addr.is_loopback) and not allow_private:
            raise ValueError("endpoint host resolves to a private address")
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
