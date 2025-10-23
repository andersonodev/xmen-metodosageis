"""Utilities for encrypting and decrypting sensitive profile information."""

from __future__ import annotations

import base64
import hashlib
from functools import lru_cache
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


@lru_cache(maxsize=1)
def _get_fernet() -> Fernet:
    """Return a configured :class:`~cryptography.fernet.Fernet` instance.

    The key is derived from ``settings.PROFILE_ENCRYPTION_KEY`` if provided,
    otherwise from the Django ``SECRET_KEY``. The derivation uses SHA-256 to
    ensure the value matches the expected 32-byte length for Fernet keys.
    """

    configured_key = getattr(settings, "PROFILE_ENCRYPTION_KEY", None)
    if configured_key:
        key_bytes = configured_key.encode("utf-8")
    else:
        key_bytes = settings.SECRET_KEY.encode("utf-8")

    digest = hashlib.sha256(key_bytes).digest()
    fernet_key = base64.urlsafe_b64encode(digest)
    return Fernet(fernet_key)


def encrypt(value: Optional[str]) -> Optional[str]:
    """Encrypt the provided value using Fernet.

    ``None`` or empty strings are returned untouched so Django can handle
    nullable fields transparently.
    """

    if value in (None, ""):
        return value

    fernet = _get_fernet()
    token = fernet.encrypt(value.encode("utf-8"))
    return token.decode("utf-8")


def decrypt(value: Optional[str]) -> Optional[str]:
    """Decrypt the provided value using Fernet.

    Any invalid tokens fail closed by returning ``None`` which prevents the
    application from exposing undecipherable data to the UI.
    """

    if value in (None, ""):
        return value

    fernet = _get_fernet()
    try:
        decrypted = fernet.decrypt(value.encode("utf-8"))
        return decrypted.decode("utf-8")
    except (InvalidToken, ValueError):
        return None
