"""Tests for logging functionality."""

import logging
from io import StringIO
from unittest.mock import patch

import pytest

from sideshift_sdk import SideShiftClient
from sideshift_sdk.logging_config import configure_logging, get_logger


def test_get_logger():
    """Test get_logger returns logger instance."""
    logger = get_logger()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "sideshift_sdk"


def test_configure_logging():
    """Test configure_logging function."""
    # Test with default handler
    configure_logging(level=logging.DEBUG)
    logger = get_logger()
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) > 0

    # Test with custom handler
    custom_handler = logging.StreamHandler(StringIO())
    configure_logging(level=logging.INFO, handler=custom_handler)
    logger = get_logger()
    assert logger.level == logging.INFO
    assert custom_handler in logger.handlers


def test_client_logging_enabled():
    """Test client with logging enabled."""
    log_output = StringIO()
    handler = logging.StreamHandler(log_output)
    handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    configure_logging(level=logging.DEBUG, handler=handler)

    client = SideShiftClient(
        secret="test-secret",
        enable_logging=True,
        log_level=logging.DEBUG,
    )

    assert client._enable_logging is True
    assert client._logger is not None


def test_client_logging_disabled():
    """Test client with logging disabled (default)."""
    client = SideShiftClient(secret="test-secret")
    assert client._enable_logging is False
    assert client._logger is not None  # Logger should still exist



