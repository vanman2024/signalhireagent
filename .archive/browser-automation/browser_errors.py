from __future__ import annotations

from .retry import async_retry


class TransientBrowserError(RuntimeError):
    """Errors that may succeed on retry (timeouts, navigation errors)."""


class PermanentBrowserError(RuntimeError):
    """Errors that will not succeed on retry (bad credentials, 2FA required)."""


def is_transient(exc: BaseException) -> bool:
    return isinstance(exc, TransientBrowserError)


def browser_retry(*, retries: int = 2):
    """Retry decorator specialized for browser automation operations."""

    return async_retry(retries=retries, exceptions=(TransientBrowserError,))

