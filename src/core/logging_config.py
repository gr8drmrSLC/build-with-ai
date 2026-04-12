"""
logging_config.py — structured logging setup.

Call setup_logging() once at application startup (in main.py or the
entry point). After that, every module uses the standard pattern:

    import logging
    logger = logging.getLogger(__name__)

    logger.info("API call completed", extra={"model": model, "cost_usd": cost})

Two formats:
  json — structured JSON per line, one record per line. Use in production
         and on EC2 where logs are ingested by CloudWatch or a log shipper.
  text — human-readable. Use locally during development.

Format is controlled by LOG_FORMAT in .env (default: json).
Level is controlled by LOG_LEVEL in .env (default: INFO).
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# JSON formatter
# ---------------------------------------------------------------------------


class _JsonFormatter(logging.Formatter):
    """
    Emits one JSON object per log record.

    Standard fields: timestamp, level, logger, message.
    Extra fields: any key/value pairs passed via the extra= argument.

    Exceptions are serialized to an 'exception' field so they are
    parseable rather than a multi-line traceback blob.
    """

    _RESERVED = frozenset(logging.LogRecord(
        "", 0, "", 0, "", (), None
    ).__dict__.keys()) | {"message", "asctime"}

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()

        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.message,
        }

        # Attach any extra= fields the caller passed
        for key, value in record.__dict__.items():
            if key not in self._RESERVED:
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


# ---------------------------------------------------------------------------
# Text formatter
# ---------------------------------------------------------------------------


class _TextFormatter(logging.Formatter):
    """
    Human-readable format for local development:
        2026-04-10T12:00:00Z  INFO  core.budget_guard — message  key=value ...
    """

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()
        ts = datetime.fromtimestamp(record.created, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        base = f"{ts}  {record.levelname:<8}  {record.name} — {record.message}"

        # Append extra= fields as key=value pairs
        reserved = logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys()
        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k not in reserved and k != "message"
        }
        if extras:
            pairs = "  ".join(f"{k}={v}" for k, v in extras.items())
            base = f"{base}  {pairs}"

        if record.exc_info:
            base = f"{base}\n{self.formatException(record.exc_info)}"

        return base


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def setup_logging(
    level: str | None = None,
    log_format: str | None = None,
) -> None:
    """
    Configure the root logger. Call once at application startup.

    Args:
        level: Override LOG_LEVEL from settings (e.g. "DEBUG" for a single run).
        log_format: Override LOG_FORMAT from settings ("json" or "text").

    Subsequent calls are no-ops — the handler is only added once.
    """
    from core.config import settings  # noqa: PLC0415 — lazy to avoid circular import

    resolved_level = (level or settings.log_level).upper()
    resolved_format = (log_format or settings.log_format).lower()

    root = logging.getLogger()

    # Avoid adding duplicate handlers if called more than once
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        _JsonFormatter() if resolved_format == "json" else _TextFormatter()
    )

    root.addHandler(handler)
    root.setLevel(resolved_level)

    # Silence noisy third-party loggers at WARNING unless debug mode
    if resolved_level != "DEBUG":
        for noisy in ("httpx", "httpcore", "anthropic", "urllib3", "botocore"):
            logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger(__name__).debug(
        "Logging configured",
        extra={"level": resolved_level, "format": resolved_format},
    )


def get_logger(name: str) -> logging.Logger:
    """
    Convenience wrapper. Equivalent to logging.getLogger(name).

    Use in modules that want an explicit import:
        from core.logging_config import get_logger
        logger = get_logger(__name__)
    """
    return logging.getLogger(name)
