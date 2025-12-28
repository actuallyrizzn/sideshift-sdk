"""Logging configuration for SideShift SDK."""

import logging
from typing import Optional

# Create logger for the SDK
logger = logging.getLogger("sideshift_sdk")
logger.addHandler(logging.NullHandler())  # Prevent propagation to root logger by default


def configure_logging(level: int | str = logging.WARNING, handler: Optional[logging.Handler] = None) -> None:
    """Configure logging for the SideShift SDK.

    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO, logging.WARNING)
        handler: Optional custom logging handler. If not provided, uses StreamHandler.

    Examples:
        >>> import logging
        >>> from sideshift_sdk.logging_config import configure_logging
        >>> configure_logging(level=logging.DEBUG)
    """
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Add handler if provided, otherwise use StreamHandler
    if handler is None:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

    logger.addHandler(handler)


def get_logger() -> logging.Logger:
    """Get the SDK logger instance.

    Returns:
        Logger instance for the SDK
    """
    return logger

