"""
smoke_test.py — baseline verification for src/core/.

Runs in under 30 seconds. Does not require a real Anthropic API key
for the core tests — a placeholder key satisfies the format validator.
If ANTHROPIC_API_KEY is a real key (not the placeholder), the live
call test will also run.

Usage:
    python tests/smoke_test.py          # run all tests, print results
    pytest tests/smoke_test.py -v       # run via pytest

All tests must pass before any change to src/core/ is committed.
A failing smoke test means the working baseline is broken — stop
and fix before proceeding. See DEVELOPMENT_PROTOCOL.md Step 1.
"""

from __future__ import annotations

import os
import sys
import time
import traceback

# Ensure src/ is on the path when running directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Provide a placeholder key if none is set — allows the import/unit tests
# to run in CI or on machines without a real key
if not os.environ.get("ANTHROPIC_API_KEY"):
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-smoke-test-placeholder-00000000"

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

_results: list[tuple[str, bool, str]] = []


def _run(name: str, fn) -> bool:  # type: ignore[type-arg]
    try:
        fn()
        _results.append((name, True, ""))
        return True
    except Exception:
        _results.append((name, False, traceback.format_exc()))
        return False


# ---------------------------------------------------------------------------
# 1. Imports
# ---------------------------------------------------------------------------


def test_imports() -> None:
    """All core modules import without error."""
    from core import (  # noqa: F401
        agent_dispatcher,
        budget_guard,
        config,
        logging_config,
        rate_limiter,
        task_schema,
    )


# ---------------------------------------------------------------------------
# 2. Config
# ---------------------------------------------------------------------------


def test_config_loads() -> None:
    """Settings load and required fields are present."""
    from core.config import get_settings

    get_settings.cache_clear()
    s = get_settings()
    assert s.anthropic_api_key.startswith("sk-ant-"), "API key format invalid"
    assert s.session_budget_usd > 0, "session_budget_usd must be > 0"
    assert s.executor_model, "executor_model must be set"
    assert s.orchestrator_model, "orchestrator_model must be set"
    assert s.log_level in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def test_config_invalid_key_rejected() -> None:
    """Config rejects a key that doesn't start with sk-ant-."""
    from pydantic import ValidationError
    from core.config import Settings

    try:
        Settings(anthropic_api_key="not-a-valid-key")
        raise AssertionError("Should have raised ValidationError")
    except ValidationError:
        pass  # expected


# ---------------------------------------------------------------------------
# 3. BudgetGuard
# ---------------------------------------------------------------------------


def test_budget_guard_check_passes() -> None:
    """BudgetGuard.check() allows a call within limits."""
    from core.budget_guard import BudgetGuard

    guard = BudgetGuard(session_limit_usd=5.00, per_call_limit_usd=0.10, per_call_token_limit=50_000)
    guard.check("claude-haiku-4-5-20251001", estimated_input=500, estimated_output=200)


def test_budget_guard_token_limit() -> None:
    """BudgetGuard.check() raises BudgetExceeded on token overrun."""
    from core.budget_guard import BudgetGuard, BudgetExceeded

    guard = BudgetGuard(per_call_token_limit=1_000)
    try:
        guard.check("claude-haiku-4-5-20251001", estimated_input=900, estimated_output=200)
        raise AssertionError("Should have raised BudgetExceeded")
    except BudgetExceeded:
        pass


def test_budget_guard_session_limit() -> None:
    """BudgetGuard blocks when session spend would be exceeded."""
    from core.budget_guard import BudgetGuard, BudgetExceeded

    guard = BudgetGuard(session_limit_usd=0.000001)
    guard.record("claude-haiku-4-5-20251001", input_tokens=100, output_tokens=50)
    try:
        guard.check("claude-haiku-4-5-20251001", estimated_input=100, estimated_output=50)
        raise AssertionError("Should have raised BudgetExceeded")
    except BudgetExceeded:
        pass


def test_budget_guard_record_accumulates() -> None:
    """BudgetGuard.session_spend accumulates across calls."""
    from core.budget_guard import BudgetGuard

    guard = BudgetGuard()
    assert guard.session_spend == 0.0
    guard.record("claude-haiku-4-5-20251001", input_tokens=1_000_000, output_tokens=0)
    assert abs(guard.session_spend - 0.25) < 0.001, f"Expected ~$0.25, got {guard.session_spend}"


# ---------------------------------------------------------------------------
# 4. RateLimiter
# ---------------------------------------------------------------------------


def test_rate_limiter_allows_burst() -> None:
    """RateLimiter allows burst calls immediately when tokens are available."""
    from core.rate_limiter import RateLimiter

    limiter = RateLimiter(rpm=60, burst=3)
    start = time.monotonic()
    limiter.acquire()
    limiter.acquire()
    limiter.acquire()
    elapsed = time.monotonic() - start
    assert elapsed < 0.5, f"Three burst calls took {elapsed:.2f}s — should be near-instant"


def test_rate_limiter_timeout() -> None:
    """RateLimiter raises TimeoutError when no token available within timeout."""
    from core.rate_limiter import RateLimiter

    limiter = RateLimiter(rpm=1, burst=1)
    limiter.acquire()  # drain
    try:
        limiter.acquire(timeout=0.05)
        raise AssertionError("Should have raised TimeoutError")
    except TimeoutError:
        pass


# ---------------------------------------------------------------------------
# 5. Task schema
# ---------------------------------------------------------------------------


def test_task_schema_defaults() -> None:
    """Task has correct defaults."""
    from core.task_schema import Task, ComplexityTier

    t = Task(description="test", user_message="hello")
    assert t.complexity == ComplexityTier.SIMPLE
    assert t.max_tokens == 1024
    assert t.id is not None


def test_task_result_ledger_row() -> None:
    """TaskResult.ledger_row() returns a pipe-delimited string."""
    from core.task_schema import Task, TaskResult, TaskStatus
    import uuid

    r = TaskResult(
        task_id=uuid.uuid4(),
        task_description="classify sentiment",
        status=TaskStatus.DONE,
        output="Positive",
        model="claude-haiku-4-5-20251001",
        input_tokens=420,
        output_tokens=12,
        cost_usd=0.000120,
    )
    row = r.ledger_row()
    assert row.startswith("|"), f"Expected pipe-delimited row, got: {row}"
    assert "Haiku" in row
    assert "Done" in row


# ---------------------------------------------------------------------------
# 6. AgentDispatcher (no real API call)
# ---------------------------------------------------------------------------


def test_dispatcher_model_selection() -> None:
    """AgentDispatcher selects correct model per ComplexityTier."""
    from core.agent_dispatcher import select_model
    from core.task_schema import Task, ComplexityTier

    assert "haiku" in select_model(Task(description="t", user_message="m", complexity=ComplexityTier.SIMPLE)).lower()
    assert "sonnet" in select_model(Task(description="t", user_message="m", complexity=ComplexityTier.COMPLEX)).lower()
    assert "opus" in select_model(Task(description="t", user_message="m", complexity=ComplexityTier.CRITICAL)).lower()


def test_dispatcher_budget_skip() -> None:
    """AgentDispatcher returns SKIPPED (not raise) when budget exceeded."""
    from core.agent_dispatcher import AgentDispatcher
    from core.budget_guard import BudgetGuard
    from core.task_schema import Task, TaskStatus

    guard = BudgetGuard(session_limit_usd=0.000001)
    dispatcher = AgentDispatcher(budget_guard=guard)
    result = dispatcher.dispatch(Task(description="test", user_message="hello"))
    assert result.status == TaskStatus.SKIPPED
    assert result.error is not None


# ---------------------------------------------------------------------------
# 7. Live API call (only if a real key is configured)
# ---------------------------------------------------------------------------


def test_live_api_call() -> None:
    """
    Makes a real Anthropic API call and verifies the response structure.
    Skipped automatically if ANTHROPIC_API_KEY is the smoke-test placeholder.
    """
    from core.config import get_settings

    get_settings.cache_clear()
    key = get_settings().anthropic_api_key
    if key == "sk-ant-smoke-test-placeholder-00000000":
        print("  (live call skipped — placeholder key)")
        return

    from core.agent_dispatcher import AgentDispatcher
    from core.task_schema import Task, TaskStatus, ComplexityTier

    dispatcher = AgentDispatcher()
    result = dispatcher.dispatch(Task(
        description="smoke test live call",
        user_message="Reply with exactly the word PONG and nothing else.",
        complexity=ComplexityTier.SIMPLE,
        max_tokens=16,
    ))
    assert result.status == TaskStatus.DONE, f"Expected DONE, got {result.status}: {result.error}"
    assert result.output is not None
    assert "PONG" in result.output.upper(), f"Expected PONG in response, got: {result.output!r}"
    print(f"  live call: {result.input_tokens}in / {result.output_tokens}out / ${result.cost_usd:.5f}")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

ALL_TESTS = [
    ("imports",                       test_imports),
    ("config loads",                  test_config_loads),
    ("config rejects invalid key",    test_config_invalid_key_rejected),
    ("budget guard check passes",     test_budget_guard_check_passes),
    ("budget guard token limit",      test_budget_guard_token_limit),
    ("budget guard session limit",    test_budget_guard_session_limit),
    ("budget guard accumulates",      test_budget_guard_record_accumulates),
    ("rate limiter burst",            test_rate_limiter_allows_burst),
    ("rate limiter timeout",          test_rate_limiter_timeout),
    ("task schema defaults",          test_task_schema_defaults),
    ("task result ledger row",        test_task_result_ledger_row),
    ("dispatcher model selection",    test_dispatcher_model_selection),
    ("dispatcher budget skip",        test_dispatcher_budget_skip),
    ("live API call",                 test_live_api_call),
]


if __name__ == "__main__":
    print("smoke_test.py — src/core/ baseline verification")
    print("=" * 52)

    passed = 0
    failed = 0

    for name, fn in ALL_TESTS:
        ok = _run(name, fn)
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")
        if not ok:
            # Print first line of traceback for quick diagnosis
            tb_lines = _results[-1][2].strip().splitlines()
            print(f"         {tb_lines[-1]}")
        if ok:
            passed += 1
        else:
            failed += 1

    print("=" * 52)
    print(f"  {passed} passed  {failed} failed")

    if failed:
        sys.exit(1)
