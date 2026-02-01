"""Structured JSON logging configuration."""

import logging
import sys
from typing import Any

import structlog


def setup_logging(debug: bool = False) -> None:
    """Configure structured logging for the application."""

    # Set log level
    log_level = logging.DEBUG if debug else logging.INFO

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if debug else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_agent_step(
    project_id: str,
    agent: str,
    step: str,
    input_data: str,
    output_summary: str,
    latency_ms: int,
    model: str,
    tokens: int,
    status: str,
) -> None:
    """Log an agent execution step with structured data."""
    logger = get_logger("agent")
    logger.info(
        "agent_step",
        project_id=project_id,
        agent=agent,
        step=step,
        input=input_data[:200] if input_data else "",  # Truncate for logging
        output_summary=output_summary[:200] if output_summary else "",
        latency_ms=latency_ms,
        model=model,
        tokens=tokens,
        status=status,
    )
