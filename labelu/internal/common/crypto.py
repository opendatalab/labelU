"""Symmetric encryption utilities for storing sensitive values (e.g. S3 credentials).

Uses Fernet (AES-128-CBC + HMAC-SHA256) with a key derived from the
application's PASSWORD_SECRET_KEY.
"""

from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet


def _derive_key(secret: str) -> bytes:
    """Derive a 32-byte Fernet-compatible key from an arbitrary secret string."""
    raw = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(raw)


def _get_fernet() -> Fernet:
    from labelu.internal.common.config import settings

    if not settings.PASSWORD_SECRET_KEY:
        raise RuntimeError(
            "PASSWORD_SECRET_KEY must be set to use credential encryption"
        )
    return Fernet(_derive_key(settings.PASSWORD_SECRET_KEY))


def encrypt_value(plaintext: str) -> str:
    """Encrypt a string and return a URL-safe base64-encoded ciphertext."""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str) -> str:
    """Decrypt a URL-safe base64-encoded ciphertext back to plaintext."""
    return _get_fernet().decrypt(ciphertext.encode()).decode()
