"""
budget_guard.py — session spend tracking and hard cap enforcement.

Enforces the spend limits defined in BUDGET_POLICY.md. Checks estimated
cost before every API call and raises BudgetExceeded if a limit would
be exceeded. Records actual usage after each call so session totals
are accurate.

Usage:
    from core.budget_guard import BudgetGuard, BudgetExceeded

    guard = BudgetGuard()  # limits from settings
    try:
        guard.check(model="claude-haiku-4-5-20251001", estimated_input=800, estimated_output=400)
    except BudgetExceeded as e:
        logger.error("Budget check failed", extra={"reason": str(e)})
        raise

    response = client.messages.create(...)
    guard.record(
        model="claude-haiku-4-5-20251001",
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model pricing table
# Prices in USD per 1,000,000 tokens. Update when Anthropic changes pricing.
# Source: https://www.anthropic.com/pricing
# ---------------------------------------------------------------------------

_MODEL_PRICING: dict[str, tuple[float, float]] = {
    # key → (input $/M, output $/M)
    "claude-opus": (15.00, 75.00),
    "claude-sonnet": (3.00, 15.00),
    "claude-haiku": (0.25, 1.25),
}

# Fallback pricing if model is not in the table — conservative (Sonnet rates)
_DEFAULT_PRICING: tuple[float, float] = (3.00, 15.00)


def _lookup_pricing(model: str) -> tuple[float, float]:
    """Return (input_price, output_price) for the given model name.

    Matches by prefix so versioned model IDs (e.g. 'claude-haiku-4-5-20251001')
    resolve to the correct pricing tier.
    """
    model_lower = model.lower()
    for key, pricing in _MODEL_PRICING.items():
        if key in model_lower:
            return pricing
    logger.warning(
        "Unknown model '%s' — using default pricing (Sonnet rates). "
        "Add to _MODEL_PRICING if this model is used regularly.",
        model,
    )
    return _DEFAULT_PRICING


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class BudgetExceeded(Exception):
    """Raised when a call would exceed a configured spend or token limit."""


# ---------------------------------------------------------------------------
# Call record
# ---------------------------------------------------------------------------


@dataclass
class CallRecord:
    """Record of a single API call, written after the call completes."""

    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    task: str = ""  # optional label for TASK_LEDGER entries


# ---------------------------------------------------------------------------
# BudgetGuard
# ---------------------------------------------------------------------------


@dataclass
class BudgetGuard:
    """
    Enforces spend limits before and after API calls.

    Limits default to values from settings if not supplied explicitly.
    Pass explicit values in tests or when a single session needs a
    different cap from the default.
    """

    session_limit_usd: float = field(default_factory=lambda: _default_session_limit())
    per_call_limit_usd: float = field(default_factory=lambda: _default_per_call_limit())
    per_call_token_limit: int = field(default_factory=lambda: _default_token_limit())

    _calls: list[CallRecord] = field(default_factory=list, init=False, repr=False)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def estimate_cost(
        self,
        model: str,
        estimated_input: int,
        estimated_output: int = 0,
    ) -> float:
        """Return estimated cost in USD for the given token counts."""
        input_price, output_price = _lookup_pricing(model)
        return (estimated_input * input_price + estimated_output * output_price) / 1_000_000

    def check(
        self,
        model: str,
        estimated_input: int,
        estimated_output: int = 0,
    ) -> None:
        """
        Check whether the proposed call is within budget.

        Raises BudgetExceeded if:
        - estimated token count exceeds per_call_token_limit
        - estimated cost exceeds per_call_limit_usd
        - session spend + estimated cost would exceed session_limit_usd

        Call this immediately before client.messages.create().
        Does not make any API call itself.
        """
        total_tokens = estimated_input + estimated_output
        if total_tokens > self.per_call_token_limit:
            raise BudgetExceeded(
                f"Estimated token count {total_tokens:,} exceeds per-call limit "
                f"{self.per_call_token_limit:,}. Reduce prompt size or confirm explicitly."
            )

        estimated_cost = self.estimate_cost(model, estimated_input, estimated_output)
        if estimated_cost > self.per_call_limit_usd:
            raise BudgetExceeded(
                f"Estimated call cost ${estimated_cost:.4f} exceeds per-call limit "
                f"${self.per_call_limit_usd:.2f}. Use a cheaper model or confirm explicitly."
            )

        projected_session_spend = self.session_spend + estimated_cost
        if projected_session_spend > self.session_limit_usd:
            raise BudgetExceeded(
                f"Projected session spend ${projected_session_spend:.4f} would exceed "
                f"session limit ${self.session_limit_usd:.2f}. "
                f"Current spend: ${self.session_spend:.4f}."
            )

        logger.debug(
            "Budget check passed",
            extra={
                "model": model,
                "estimated_input_tokens": estimated_input,
                "estimated_output_tokens": estimated_output,
                "estimated_cost_usd": estimated_cost,
                "session_spend_usd": self.session_spend,
            },
        )

    def record(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        task: str = "",
    ) -> CallRecord:
        """
        Record actual usage after a completed API call.

        Call this immediately after client.messages.create() returns,
        using response.usage.input_tokens and response.usage.output_tokens.
        Returns the CallRecord so callers can log it to TASK_LEDGER if needed.
        """
        cost = self.estimate_cost(model, input_tokens, output_tokens)
        record = CallRecord(
            timestamp=datetime.now(tz=timezone.utc),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            task=task,
        )
        self._calls.append(record)
        logger.info(
            "API call recorded",
            extra={
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost,
                "session_spend_usd": self.session_spend,
                "task": task,
            },
        )
        return record

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def session_spend(self) -> float:
        """Total spend recorded so far this session, in USD."""
        return sum(c.cost_usd for c in self._calls)

    @property
    def calls(self) -> list[CallRecord]:
        """Immutable view of all recorded calls this session."""
        return list(self._calls)

    def summary(self) -> str:
        """Human-readable session spend summary."""
        lines = [
            f"Session spend: ${self.session_spend:.4f} / ${self.session_limit_usd:.2f}",
            f"Calls recorded: {len(self._calls)}",
        ]
        for i, call in enumerate(self._calls, 1):
            lines.append(
                f"  {i}. {call.model} — "
                f"{call.input_tokens}in / {call.output_tokens}out — "
                f"${call.cost_usd:.4f}"
                + (f" [{call.task}]" if call.task else "")
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Default value helpers — read from settings lazily to avoid circular import
# ---------------------------------------------------------------------------


def _default_session_limit() -> float:
    from core.config import settings  # noqa: PLC0415

    return settings.session_budget_usd


def _default_per_call_limit() -> float:
    from core.config import settings  # noqa: PLC0415

    return settings.per_call_budget_usd


def _default_token_limit() -> int:
    from core.config import settings  # noqa: PLC0415

    return settings.per_call_token_limit
