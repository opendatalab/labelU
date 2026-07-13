import pytest
from pydantic import ValidationError

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
    """Regression tests: the S3 endpoint must not point at internal targets."""

    @pytest.mark.parametrize(
        "endpoint",
        [
            "http://169.254.169.254",          # cloud metadata (IMDS)
            "http://169.254.169.254/latest/",  # IMDS with path
            "http://127.0.0.1:9000",           # loopback
            "http://localhost:9000",           # loopback by name
            "http://10.1.2.3",                 # private range
            "http://192.168.0.1",              # private range
            "http://172.16.5.5",               # private range
            "http://[::1]:9000",               # IPv6 loopback
            "file:///etc/passwd",              # non-http scheme
            "ftp://example.com",               # non-http scheme
            "http://0.0.0.0",                  # unspecified
        ],
    )
    def test_rejects_internal_or_bad_scheme_endpoint(self, endpoint):
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
