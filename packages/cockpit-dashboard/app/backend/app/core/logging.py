import structlog

from app.core.config import settings


def setup_logging() -> None:
    if settings.LOG_FORMAT == "json":
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(20),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
        )
    else:
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.dev.ConsoleRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(20),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
        )
