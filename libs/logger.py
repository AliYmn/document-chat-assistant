import logging
import sys
import time

import structlog
from pythonjsonlogger import jsonlogger
from rich.console import Console
from rich.logging import RichHandler

from libs.settings import settings


def configure_logging(service_name: str, log_level: str = "INFO") -> None:
    """
    Configure structured logging for the application.

    Args:
        service_name: Name of the service (auth_service, pdf_service, etc.)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Set log level
    log_level_value = getattr(logging, log_level.upper())

    # Configure structlog
    structlog.configure(
        processors=[
            # Add log level name
            structlog.stdlib.add_log_level,
            # Add timestamp
            structlog.processors.TimeStamper(fmt="iso"),
            # Add caller info (file, line number)
            structlog.processors.CallsiteParameterAdder(
                parameters={
                    structlog.processors.CallsiteParameter.PATHNAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                }
            ),
            # Add service name
            structlog.processors.StackInfoRenderer(),
            # If in development, format logs for console readability
            structlog.dev.ConsoleRenderer()
            if settings.ENV_NAME == "development"
            else structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    handlers = []

    # Console handler with rich formatting for development
    if settings.ENV_NAME == "development":
        console = Console(width=120)
        handlers.append(RichHandler(console=console, rich_tracebacks=True, tracebacks_show_locals=True))
    else:
        # JSON handler for production
        json_handler = logging.StreamHandler(sys.stdout)
        json_formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            json_default=str,
        )
        json_handler.setFormatter(json_formatter)
        handlers.append(json_handler)

    # Configure root logger
    logging.basicConfig(
        level=log_level_value,
        handlers=handlers,
        format="%(message)s",
        datefmt="[%X]",
        force=True,
    )

    # Set log level for other libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    # Create a logger with service name
    logger = structlog.get_logger(service_name)
    logger.info(f"{service_name} logging configured", log_level=log_level)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (usually module or class name)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


class LoggingMiddleware:
    """
    Middleware for logging HTTP requests and responses.
    """

    def __init__(self, app):
        self.app = app
        self.logger = get_logger("http")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        start_time = time.time()

        # Extract request information
        method = scope.get("method", "")
        path = scope.get("path", "")
        query_string = scope.get("query_string", b"").decode("utf-8")
        client = scope.get("client", ("", 0))
        client_host = client[0] if client else ""

        # Log request
        self.logger.info(
            "Request started",
            method=method,
            path=path,
            query_string=query_string,
            client_host=client_host,
        )

        # Process request
        response_started = False
        status_code = 0

        async def send_wrapper(message):
            nonlocal response_started, status_code
            if message["type"] == "http.response.start":
                response_started = True
                status_code = message.get("status", 0)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            self.logger.exception("Request failed", error=str(e))
            raise
        finally:
            # Calculate request duration
            duration_ms = round((time.time() - start_time) * 1000, 2)

            # Log response
            log_method = self.logger.info if status_code < 500 else self.logger.error
            log_method(
                "Request finished",
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=duration_ms,
            )
