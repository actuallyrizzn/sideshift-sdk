"""Tests for configuration management."""

import os
from unittest.mock import patch

import pytest

from sideshift_sdk import SideShiftClient, AsyncSideShiftClient
from sideshift_sdk.config import SDKConfig
from sideshift_sdk.constants import BASE_URL


def test_config_default_timeout():
    """Test default timeout value."""
    assert SDKConfig.DEFAULT_TIMEOUT == 30


def test_config_default_max_retries():
    """Test default max retries value."""
    assert SDKConfig.DEFAULT_MAX_RETRIES == 3


def test_config_default_base_url():
    """Test default base URL value."""
    assert SDKConfig.DEFAULT_BASE_URL == BASE_URL


def test_get_timeout_from_provided():
    """Test getting timeout from provided value."""
    assert SDKConfig.get_timeout(60) == 60
    assert SDKConfig.get_timeout(10) == 10


def test_get_timeout_from_env():
    """Test getting timeout from environment variable."""
    with patch.dict(os.environ, {"SIDESHIFT_TIMEOUT": "45"}):
        assert SDKConfig.get_timeout() == 45


def test_get_timeout_default():
    """Test getting default timeout when nothing provided."""
    with patch.dict(os.environ, {}, clear=True):
        # Remove SIDESHIFT_TIMEOUT if it exists
        os.environ.pop("SIDESHIFT_TIMEOUT", None)
        assert SDKConfig.get_timeout() == SDKConfig.DEFAULT_TIMEOUT


def test_get_timeout_provided_overrides_env():
    """Test that provided timeout overrides environment variable."""
    with patch.dict(os.environ, {"SIDESHIFT_TIMEOUT": "45"}):
        assert SDKConfig.get_timeout(60) == 60


def test_get_max_retries_from_provided():
    """Test getting max retries from provided value."""
    assert SDKConfig.get_max_retries(5) == 5
    assert SDKConfig.get_max_retries(1) == 1


def test_get_max_retries_from_env():
    """Test getting max retries from environment variable."""
    with patch.dict(os.environ, {"SIDESHIFT_MAX_RETRIES": "5"}):
        assert SDKConfig.get_max_retries() == 5


def test_get_max_retries_default():
    """Test getting default max retries when nothing provided."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("SIDESHIFT_MAX_RETRIES", None)
        assert SDKConfig.get_max_retries() == SDKConfig.DEFAULT_MAX_RETRIES


def test_get_base_url_from_provided():
    """Test getting base URL from provided value."""
    custom_url = "https://custom.example.com/api"
    assert SDKConfig.get_base_url(custom_url) == custom_url


def test_get_base_url_from_env():
    """Test getting base URL from environment variable."""
    custom_url = "https://custom.example.com/api"
    with patch.dict(os.environ, {"SIDESHIFT_BASE_URL": custom_url}):
        assert SDKConfig.get_base_url() == custom_url


def test_get_base_url_default():
    """Test getting default base URL when nothing provided."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("SIDESHIFT_BASE_URL", None)
        assert SDKConfig.get_base_url() == SDKConfig.DEFAULT_BASE_URL


def test_client_uses_config_timeout():
    """Test that client uses configurable timeout."""
    client = SideShiftClient(secret="test-secret", timeout=60)
    assert client.timeout == 60


def test_client_uses_config_base_url():
    """Test that client uses configurable base URL."""
    custom_url = "https://custom.example.com/api"
    client = SideShiftClient(secret="test-secret", base_url=custom_url)
    assert client.base_url == custom_url


def test_client_uses_env_timeout():
    """Test that client uses timeout from environment variable."""
    with patch.dict(os.environ, {"SIDESHIFT_TIMEOUT": "45"}):
        client = SideShiftClient(secret="test-secret")
        assert client.timeout == 45


def test_client_uses_env_base_url():
    """Test that client uses base URL from environment variable."""
    custom_url = "https://custom.example.com/api"
    with patch.dict(os.environ, {"SIDESHIFT_BASE_URL": custom_url}):
        client = SideShiftClient(secret="test-secret")
        assert client.base_url == custom_url


def test_client_provided_overrides_env():
    """Test that provided values override environment variables."""
    with patch.dict(os.environ, {"SIDESHIFT_TIMEOUT": "45", "SIDESHIFT_BASE_URL": "https://env.example.com"}):
        client = SideShiftClient(secret="test-secret", timeout=60, base_url="https://provided.example.com")
        assert client.timeout == 60
        assert client.base_url == "https://provided.example.com"


@pytest.mark.asyncio
async def test_async_client_uses_config():
    """Test that async client uses configurable values."""
    async with AsyncSideShiftClient(secret="test-secret", timeout=60) as client:
        assert client.timeout == 60

