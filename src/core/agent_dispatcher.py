"""
agent_dispatcher.py — model selection, budget check, and API dispatch.

The central call point for all agent invocations. Takes a Task,
selects the right model, checks budget and rate limits, calls the
Anthropic API, records usage, and returns a TaskResult.

Usage:
    from core.agent_dispatcher import AgentDispatcher
    from core.task_schema import Task, ComplexityTier

    dispatcher = AgentDispatcher()

    result = dispatcher.dispatch(Task(
        description="classify sentiment",
        user_message="Is this review positive or negative? 'Great product!'",
        complexity=ComplexityTier.SIMPLE,
    ))

    if result.status == TaskStatus.DONE:
        print(result.output)
    print(result.ledger_row())

The dispatcher instance holds BudgetGuard and RateLimiter state across
calls, so session spend and rate limiting are tracked correctly when
dispatching multiple tasks in a session.
"""

from __future__ import annotations

import logging

import anthropic

from core.budget_guard import BudgetGuard, BudgetExceeded
from core.config import settings
from core.rate_limiter import RateLimiter
from core.task_schema import ComplexityTier, Task, TaskResult, TaskStatus

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model selection
# ---------------------------------------------------------------------------

# Maps ComplexityTier to model. Overridable per-task via Task.model.
# Sourced from settings so .env controls defaults without code changes.
_TIER_TO_MODEL: dict[ComplexityTier, str] = {
    ComplexityTier.SIMPLE: settings.executor_model,        # Haiku — cheap, fast
    ComplexityTier.COMPLEX: settings.orchestrator_model,   # Sonnet — reasoning
    ComplexityTier.CRITICAL: "claude-opus-4-6",            # Opus — hard to reverse decisions
}

# Conservative output token estimates per tier, used for pre-call budget check.
# The actual output is usually less; this prevents false budget blocks on short tasks.
_TIER_OUTPUT_ESTIMATE: dict[ComplexityTier, int] = {
    ComplexityTier.SIMPLE: 256,
    ComplexityTier.COMPLEX: 1024,
    ComplexityTier.CRITICAL: 2048,
}


def select_model(task: Task) -> str:
    """Return the model to use for this task.

    Uses Task.model if explicitly set; otherwise derives from complexity tier.
    """
    if task.model:
        return task.model
    return _TIER_TO_MODEL[task.complexity]


# ---------------------------------------------------------------------------
# AgentDispatcher
# ---------------------------------------------------------------------------


class AgentDispatcher:
    """
    Dispatches tasks to the Anthropic API with budget and rate enforcement.

    Maintains BudgetGuard and RateLimiter state across calls — instantiate
    once per session, reuse for all tasks in that session.

    Args:
        budget_guard:  Custom BudgetGuard instance. Defaults to one built
                       from settings (session limit, per-call limit).
        rate_limiter:  Custom RateLimiter instance. Defaults to one built
                       from settings (requests_per_minute).
        default_system: System prompt used when Task.system_prompt is None.
    """

    _DEFAULT_SYSTEM = (
        "You are a precise, efficient AI assistant. "
        "Complete the requested task. Be concise. Do not add commentary "
        "beyond what was asked."
    )

    def __init__(
        self,
        budget_guard: BudgetGuard | None = None,
        rate_limiter: RateLimiter | None = None,
        default_system: str | None = None,
    ) -> None:
        self._guard = budget_guard or BudgetGuard()
        self._limiter = rate_limiter or RateLimiter()
        self._default_system = default_system or self._DEFAULT_SYSTEM
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def dispatch(self, task: Task) -> TaskResult:
        """
        Execute a task and return its result.

        Never raises — all exceptions are caught and returned as a
        TaskResult with status=FAILED or status=SKIPPED. Check
        result.status before using result.output.
        """
        model = select_model(task)
        system = task.system_prompt or self._default_system
        estimated_input = _estimate_input_tokens(system, task.user_message)
        estimated_output = _TIER_OUTPUT_ESTIMATE[task.complexity]

        logger.info(
            "Dispatching task",
            extra={
                "task_id": str(task.id),
                "description": task.description,
                "model": model,
                "complexity": task.complexity.value,
                "estimated_input_tokens": estimated_input,
            },
        )

        # --- Budget check ---
        try:
            self._guard.check(model, estimated_input, estimated_output)
        except BudgetExceeded as e:
            logger.warning(
                "Task skipped — budget exceeded",
                extra={"task_id": str(task.id), "reason": str(e)},
            )
            return TaskResult(
                task_id=task.id,
                task_description=task.description,
                status=TaskStatus.SKIPPED,
                error=str(e),
            )

        # --- Rate limit ---
        try:
            self._limiter.acquire()
        except TimeoutError as e:
            logger.warning(
                "Task failed — rate limit timeout",
                extra={"task_id": str(task.id), "reason": str(e)},
            )
            return TaskResult(
                task_id=task.id,
                task_description=task.description,
                status=TaskStatus.FAILED,
                error=str(e),
            )

        # --- API call ---
        try:
            response = self._client.messages.create(
                model=model,
                max_tokens=task.max_tokens,
                system=system,
                messages=[{"role": "user", "content": task.user_message}],
            )
        except anthropic.APIStatusError as e:
            logger.error(
                "Anthropic API error",
                extra={
                    "task_id": str(task.id),
                    "status_code": e.status_code,
                    "error": str(e),
                },
            )
            return TaskResult(
                task_id=task.id,
                task_description=task.description,
                status=TaskStatus.FAILED,
                error=f"API error {e.status_code}: {e.message}",
            )
        except anthropic.APIConnectionError as e:
            logger.error(
                "Anthropic connection error",
                extra={"task_id": str(task.id), "error": str(e)},
            )
            return TaskResult(
                task_id=task.id,
                task_description=task.description,
                status=TaskStatus.FAILED,
                error=f"Connection error: {e}",
            )

        # --- Record usage ---
        usage = response.usage
        self._guard.record(
            model=model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            task=task.description,
        )

        output = response.content[0].text if response.content else ""

        logger.info(
            "Task completed",
            extra={
                "task_id": str(task.id),
                "description": task.description,
                "model": model,
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "stop_reason": response.stop_reason,
            },
        )

        from core.budget_guard import _lookup_pricing  # noqa: PLC0415

        input_price, output_price = _lookup_pricing(model)
        cost = (
            usage.input_tokens * input_price + usage.output_tokens * output_price
        ) / 1_000_000

        return TaskResult(
            task_id=task.id,
            task_description=task.description,
            status=TaskStatus.DONE,
            output=output,
            model=model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cost_usd=cost,
        )

    # ------------------------------------------------------------------
    # Session state
    # ------------------------------------------------------------------

    @property
    def session_spend(self) -> float:
        """Total spend recorded this session."""
        return self._guard.session_spend

    def session_summary(self) -> str:
        """Human-readable summary of session spend and calls."""
        return self._guard.summary()


# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------


def _estimate_input_tokens(system: str, user_message: str) -> int:
    """Rough token estimate for a prompt: ~0.75 tokens per word (conservative)."""
    word_count = len((system + " " + user_message).split())
    return int(word_count / 0.75)
