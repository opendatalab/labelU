import pytest

from labelu.internal.common.config import settings
from labelu.internal.common.storage import LocalStorageBackend
from labelu.internal.common.error_code import LabelUException


class TestLocalStorageResolveTraversal:
    """Regression tests for path traversal in LocalStorageBackend._resolve."""

    def test_resolve_rejects_parent_traversal(self):
        backend = LocalStorageBackend()
        with pytest.raises(LabelUException):
            backend._resolve("../../../../../../../../etc/passwd")

    def test_resolve_rejects_nested_traversal(self):
        backend = LocalStorageBackend()
        with pytest.raises(LabelUException):
            backend._resolve("upload/1/../../../../../../../../etc/passwd")

    def test_resolve_rejects_absolute_escape(self):
        # lstrip("/") turns "/etc/passwd" into "etc/passwd" (stays inside root),
        # but a backslash-free absolute traversal must still be contained.
        backend = LocalStorageBackend()
        resolved = backend._resolve("/etc/passwd")
        assert str(resolved).startswith(str(settings.MEDIA_ROOT.resolve()))

    def test_resolve_allows_normal_key(self):
        backend = LocalStorageBackend()
        resolved = backend._resolve("upload/1/test.png")
        assert str(resolved).startswith(str(settings.MEDIA_ROOT.resolve()))
        assert resolved.name == "test.png"
