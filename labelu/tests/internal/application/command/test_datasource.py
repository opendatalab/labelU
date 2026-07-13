import pytest
from pydantic import ValidationError

from labelu.internal.common.config import settings
from labelu.internal.application.command.datasource import (
    CreateDataSourceCommand,
    UpdateDataSourceCommand,
)


def _create(endpoint):
    return CreateDataSourceCommand(
        name="ds",
        bucket="b",
        access_key_id="ak",
        secret_access_key="sk",
        endpoint=endpoint,
    )


class TestDataSourceEndpointSSRF:
    """Regression tests for the data-source S3 endpoint SSRF guard."""

    @pytest.mark.parametrize(
        "endpoint",
        [
            "http://169.254.169.254",          # AWS/GCP/Azure metadata (IMDS) - link-local
            "http://169.254.169.254/latest/",  # IMDS with path
            "http://100.100.100.200/latest/",  # Alibaba/Tencent cloud metadata (100.64.0.0/10)
            "http://100.64.0.1:9000",          # RFC6598 shared address space
            "http://0.0.0.0",                  # unspecified - always blocked
            "file:///etc/passwd",              # non-http scheme
            "ftp://example.com",               # non-http scheme
            "s3.example.com",                  # missing scheme
        ],
    )
    def test_always_rejects_metadata_and_bad_scheme(self, endpoint):
        with pytest.raises(ValidationError):
            _create(endpoint)
        with pytest.raises(ValidationError):
            UpdateDataSourceCommand(endpoint=endpoint)

    @pytest.mark.parametrize(
        "endpoint",
        [
            None,                              # optional -> AWS default
            "https://8.8.8.8:9000",            # public IP literal
            "http://1.1.1.1",                  # public IP literal
        ],
    )
    def test_allows_public_endpoint(self, endpoint):
        cmd = _create(endpoint)
        assert cmd.endpoint == endpoint

    @pytest.mark.parametrize(
        "endpoint",
        [
            "http://10.1.2.3:9000",            # private RFC1918
            "http://192.168.0.10:9000",        # private RFC1918
            "http://172.16.5.5:9000",          # private RFC1918
            "http://127.0.0.1:9000",           # loopback (same-host MinIO)
            "http://[::1]:9000",               # IPv6 loopback
            "http://localhost:9000",           # loopback by name (same-host MinIO)
        ],
    )
    def test_allows_private_endpoint_by_default(self, endpoint):
        # ALLOW_PRIVATE_S3_ENDPOINT defaults to True for on-prem deployments
        assert settings.ALLOW_PRIVATE_S3_ENDPOINT is True
        cmd = _create(endpoint)
        assert cmd.endpoint == endpoint

    @pytest.mark.parametrize(
        "endpoint",
        [
            "http://10.1.2.3:9000",
            "http://192.168.0.10:9000",
            "http://127.0.0.1:9000",
            "http://localhost:9000",
        ],
    )
    def test_strict_mode_rejects_private(self, endpoint, monkeypatch):
        monkeypatch.setattr(settings, "ALLOW_PRIVATE_S3_ENDPOINT", False)
        with pytest.raises(ValidationError):
            _create(endpoint)

    def test_strict_mode_still_allows_public(self, monkeypatch):
        monkeypatch.setattr(settings, "ALLOW_PRIVATE_S3_ENDPOINT", False)
        cmd = _create("https://8.8.8.8:9000")
        assert cmd.endpoint == "https://8.8.8.8:9000"

    def test_metadata_blocked_even_when_private_allowed(self):
        # the flag must not re-open the cloud metadata endpoint
        assert settings.ALLOW_PRIVATE_S3_ENDPOINT is True
        with pytest.raises(ValidationError):
            _create("http://169.254.169.254")
