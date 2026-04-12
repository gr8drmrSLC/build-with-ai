"""
task_schema.py — Pydantic models for tasks and results.

These are the data contracts between the orchestrator and any agent
call. Everything dispatched through agent_dispatcher.py is a Task.
Everything that comes back is a TaskResult.

Keeping the schema in one place means every module that touches tasks
imports from here — no duplicated field definitions, no drift between
what was sent and what was recorded.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TaskStatus(str, Enum):
    """Lifecycle states for a task."""

    PENDING = "pending"       # created, not yet dispatched
    RUNNING = "running"       # dispatched, awaiting result
    DONE = "done"             # completed successfully
    FAILED = "failed"         # call failed or raised an exception
    CANCELLED = "cancelled"   # aborted before completion
    SKIPPED = "skipped"       # budget/rate check prevented dispatch


class ComplexityTier(str, Enum):
    """
    Complexity classification for a task.

    Drives model selection in agent_dispatcher.py — Simple tasks go to
    Haiku, Complex tasks go to Sonnet, Critical tasks go to Opus.
    See AI_DELEGATION_POLICY.md for the full selection matrix.
    """

    SIMPLE = "simple"       # atomic, well-scoped, clear correct answer → Haiku
    COMPLEX = "complex"     # multi-step reasoning or judgment required → Sonnet
    CRITICAL = "critical"   # founding architectural decision, hard to reverse → Opus


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------


class Task(BaseModel):
    """
    A unit of work dispatched to an agent.

    The minimum viable task is a description + user_message. All other
    fields have defaults that agent_dispatcher.py fills in based on
    complexity tier and project settings.
    """

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    # What the task is
    description: str = Field(
        ...,
        description="One-line label used in logs and TASK_LEDGER entries.",
    )
    user_message: str = Field(
        ...,
        description="The user-turn message sent to the model.",
    )
    system_prompt: str | None = Field(
        default=None,
        description="System prompt. If None, agent_dispatcher uses the project default.",
    )

    # How to run it
    complexity: ComplexityTier = Field(
        default=ComplexityTier.SIMPLE,
        description="Drives model selection. Default: Simple → Haiku.",
    )
    model: str | None = Field(
        default=None,
        description=(
            "Override model selection. If set, used directly regardless of complexity. "
            "Use sparingly — prefer letting complexity tier drive selection."
        ),
    )
    max_tokens: int = Field(
        default=1024,
        description="Maximum output tokens for this call.",
        gt=0,
        le=8192,
    )

    # Context the agent needs (but the orchestrator session does not)
    context: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Additional context the agent needs to complete the task. "
            "Keep minimal — only what changes the output."
        ),
    )

    # Metadata
    tags: list[str] = Field(
        default_factory=list,
        description="Optional labels for filtering TASK_LEDGER entries.",
    )


# ---------------------------------------------------------------------------
# TaskResult
# ---------------------------------------------------------------------------


class TaskResult(BaseModel):
    """
    The outcome of a dispatched task.

    Always returned by agent_dispatcher.dispatch(), whether the call
    succeeded or failed. Check status before using output.
    """

    task_id: UUID
    task_description: str

    status: TaskStatus
    output: str | None = Field(
        default=None,
        description="Model response text. None if status is not DONE.",
    )
    error: str | None = Field(
        default=None,
        description="Error message if status is FAILED or CANCELLED.",
    )

    # Usage — populated from response.usage after a successful call
    model: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0

    completed_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    def ledger_row(self) -> str:
        """
        Format this result as a TASK_LEDGER.md table row.

        | Date       | Session | Task          | Model  | Input | Output | Cost  | Outcome |
        """
        date = self.completed_at.strftime("%Y-%m-%d")
        model = (self.model or "unknown").split("-")
        # Shorten model name for table readability: claude-haiku-4-5-... → Haiku
        short_model = next(
            (part.capitalize() for part in model if part in {"haiku", "sonnet", "opus"}),
            self.model or "unknown",
        )
        return (
            f"| {date} | — | {self.task_description[:40]} | {short_model} "
            f"| {self.input_tokens:,} | {self.output_tokens:,} "
            f"| ${self.cost_usd:.4f} | {self.status.value.capitalize()} |"
        )
