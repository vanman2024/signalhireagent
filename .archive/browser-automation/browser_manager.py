from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .browser_errors import browser_retry

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class BrowserSession:
    """Manage lifecycle of a browser automation session.

    Parameters
    - factory: async callable returning an initialized browser/session object
    - retries: number of retries for transient start-up failures
    """

    def __init__(self, factory: Callable[[], Awaitable[Any]], *, retries: int = 2) -> None:
        self._factory = factory
        self._retries = retries
        self.browser: Any | None = None

    async def __aenter__(self) -> Any:
        start = browser_retry(retries=self._retries)(self._factory)
        self.browser = await start()
        return self.browser

    async def __aexit__(self, exc_type, exc, tb) -> None:
        b = self.browser
        self.browser = None
        if b is None:
            return
        close = getattr(b, "close", None)
        if close is None:
            return
        if callable(close):
            res = close()
            if hasattr(res, "__await__"):
                await res

