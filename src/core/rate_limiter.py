"""
rate_limiter.py — token bucket for API call throttling.

Prevents hitting Anthropic's rate limits by spacing calls within a
configurable requests-per-minute window. Uses a token bucket algorithm:
tokens refill continuously, one per (60 / rpm) seconds. A call that
arrives when no tokens are available blocks until one refills.

Usage:
    from core.rate_limiter import RateLimiter

    limiter = RateLimiter()  # rpm from settings
    limiter.acquire()        # blocks if needed, then returns
    response = client.messages.create(...)

For async code, use the async variant:
    await limiter.acquire_async()
"""

from __future__ import annotations

import asyncio
import logging
import threading
import time

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Thread-safe token bucket rate limiter.

    Tokens refill at a constant rate of `rpm / 60` per second up to a
    maximum of `burst` tokens. Each acquire() call consumes one token.
    If no token is available, the call blocks until one refills.

    Args:
        rpm:   Maximum requests per minute. Defaults to settings.requests_per_minute.
        burst: Maximum tokens that can accumulate (handles short bursts).
               Defaults to min(rpm, 10) — enough to absorb a quick sequence
               of calls without throttling, but not enough to dump the full
               minute's budget at once.
    """

    def __init__(
        self,
        rpm: int | None = None,
        burst: int | None = None,
    ) -> None:
        resolved_rpm = rpm if rpm is not None else _default_rpm()
        if resolved_rpm <= 0:
            raise ValueError(f"rpm must be > 0, got {resolved_rpm}")

        self._rpm = resolved_rpm
        self._refill_rate = resolved_rpm / 60.0  # tokens per second
        self._burst = burst if burst is not None else min(resolved_rpm, 10)
        self._tokens = float(self._burst)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Synchronous API
    # ------------------------------------------------------------------

    def acquire(self, timeout: float | None = None) -> None:
        """
        Consume one token, blocking until one is available.

        Args:
            timeout: Maximum seconds to wait. Raises TimeoutError if
                     the token does not become available in time.
                     None (default) waits indefinitely.

        Raises:
            TimeoutError: If timeout is set and no token available in time.
        """
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    logger.debug(
                        "Rate limiter token consumed",
                        extra={"tokens_remaining": self._tokens, "rpm": self._rpm},
                    )
                    return
                wait = (1.0 - self._tokens) / self._refill_rate

            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError(
                        f"Rate limiter: no token available within {timeout}s "
                        f"(limit: {self._rpm} rpm)"
                    )
                wait = min(wait, remaining)

            logger.debug(
                "Rate limiter throttling",
                extra={"wait_seconds": round(wait, 3), "rpm": self._rpm},
            )
            time.sleep(wait)

    # ------------------------------------------------------------------
    # Async API
    # ------------------------------------------------------------------

    async def acquire_async(self, timeout: float | None = None) -> None:
        """
        Async variant of acquire(). Uses asyncio.sleep() instead of
        time.sleep() so it does not block the event loop.
        """
        deadline = None if timeout is None else asyncio.get_event_loop().time() + timeout
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
                wait = (1.0 - self._tokens) / self._refill_rate

            if deadline is not None:
                remaining = deadline - asyncio.get_event_loop().time()
                if remaining <= 0:
                    raise TimeoutError(
                        f"Rate limiter: no token available within {timeout}s "
                        f"(limit: {self._rpm} rpm)"
                    )
                wait = min(wait, remaining)

            await asyncio.sleep(wait)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def available_tokens(self) -> float:
        """Current token count (refilled to present moment)."""
        with self._lock:
            self._refill()
            return self._tokens

    @property
    def rpm(self) -> int:
        return self._rpm

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _refill(self) -> None:
        """Add tokens based on elapsed time. Must be called under self._lock."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._burst, self._tokens + elapsed * self._refill_rate)
        self._last_refill = now


# ---------------------------------------------------------------------------
# Default value helper — reads from settings lazily
# ---------------------------------------------------------------------------


def _default_rpm() -> int:
    from core.config import settings  # noqa: PLC0415

    return settings.requests_per_minute
