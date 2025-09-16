from __future__ import annotations

from typing import TYPE_CHECKING

from signalhire_agent.lib.rate_limiter import AsyncTokenBucket

if TYPE_CHECKING:
    from collections.abc import Callable


class RateLimiterService:
    """Service layer wrapper around AsyncTokenBucket for application use.

    Exposes a small surface for throttling API/browser operations.
    """

    def __init__(
        self,
        *,
        capacity: int,
        refill_rate: float,
        time_fn: Callable[[], float] | None = None,
    ) -> None:
        self._bucket = AsyncTokenBucket(
            capacity=capacity, refill_rate=refill_rate, time_fn=time_fn
        )

    @property
    def available(self) -> float:
        return self._bucket.available

    async def acquire(self, n: float = 1.0) -> None:
        await self._bucket.acquire(n)
