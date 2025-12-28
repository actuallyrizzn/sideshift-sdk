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


def test_get_max_connections_from_provided():
    """Test getting max connections from provided value."""
    assert SDKConfig.get_max_connections(20) == 20
    assert SDKConfig.get_max_connections(5) == 5


def test_get_max_connections_from_env():
    """Test getting max connections from environment variable."""
    with patch.dict(os.environ, {"SIDESHIFT_MAX_CONNECTIONS": "15"}):
        assert SDKConfig.get_max_connections() == 15


def test_get_max_connections_default():
    """Test getting default max connections when nothing provided."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("SIDESHIFT_MAX_CONNECTIONS", None)
        assert SDKConfig.get_max_connections() == SDKConfig.DEFAULT_MAX_CONNECTIONS


def test_get_max_keepalive_connections_from_provided():
    """Test getting max keepalive connections from provided value."""
    assert SDKConfig.get_max_keepalive_connections(10) == 10
    assert SDKConfig.get_max_keepalive_connections(3) == 3


def test_get_max_keepalive_connections_from_env():
    """Test getting max keepalive connections from environment variable."""
    with patch.dict(os.environ, {"SIDESHIFT_MAX_KEEPALIVE_CONNECTIONS": "8"}):
        assert SDKConfig.get_max_keepalive_connections() == 8


def test_get_max_keepalive_connections_default():
    """Test getting default max keepalive connections when nothing provided."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("SIDESHIFT_MAX_KEEPALIVE_CONNECTIONS", None)
        assert SDKConfig.get_max_keepalive_connections() == SDKConfig.DEFAULT_MAX_KEEPALIVE_CONNECTIONS


def test_client_uses_config_pooling():
    """Test that client uses configurable connection pooling."""
    client = SideShiftClient(secret="test-secret", max_connections=20, max_keepalive_connections=10)
    assert client.max_connections == 20
    assert client.max_keepalive_connections == 10


def test_client_uses_env_pooling():
    """Test that client uses connection pooling from environment variables."""
    with patch.dict(os.environ, {"SIDESHIFT_MAX_CONNECTIONS": "15", "SIDESHIFT_MAX_KEEPALIVE_CONNECTIONS": "8"}):
        client = SideShiftClient(secret="test-secret")
        assert client.max_connections == 15
        assert client.max_keepalive_connections == 8


@pytest.mark.asyncio
async def test_async_client_uses_config_pooling():
    """Test that async client uses configurable connection pooling."""
    async with AsyncSideShiftClient(secret="test-secret", max_connections=20, max_keepalive_connections=10) as client:
        assert client.max_connections == 20
        assert client.max_keepalive_connections == 10
        # Verify client can be created with these settings
        await client._get_client()
        assert client._client is not None


def test_get_verify_ssl_from_provided():
    """Test getting SSL verification from provided value."""
    assert SDKConfig.get_verify_ssl(True) is True
    assert SDKConfig.get_verify_ssl(False) is False


def test_get_verify_ssl_from_env():
    """Test getting SSL verification from environment variable."""
    with patch.dict(os.environ, {"SIDESHIFT_VERIFY_SSL": "false"}):
        assert SDKConfig.get_verify_ssl() is False
    with patch.dict(os.environ, {"SIDESHIFT_VERIFY_SSL": "true"}):
        assert SDKConfig.get_verify_ssl() is True
    with patch.dict(os.environ, {"SIDESHIFT_VERIFY_SSL": "1"}):
        assert SDKConfig.get_verify_ssl() is True


def test_get_verify_ssl_default():
    """Test getting default SSL verification when nothing provided."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("SIDESHIFT_VERIFY_SSL", None)
        assert SDKConfig.get_verify_ssl() is True  # Default is True for security


def test_client_uses_config_verify_ssl():
    """Test that client uses configurable SSL verification."""
    client = SideShiftClient(secret="test-secret", verify_ssl=False)
    assert client.verify_ssl is False


def test_client_uses_env_verify_ssl():
    """Test that client uses SSL verification from environment variable."""
    with patch.dict(os.environ, {"SIDESHIFT_VERIFY_SSL": "false"}):
        client = SideShiftClient(secret="test-secret")
        assert client.verify_ssl is False


@pytest.mark.asyncio
async def test_async_client_uses_config_verify_ssl():
    """Test that async client uses configurable SSL verification."""
    async with AsyncSideShiftClient(secret="test-secret", verify_ssl=False) as client:
        assert client.verify_ssl is False


def test_get_proxy_from_provided():
    """Test getting proxy from provided value."""
    assert SDKConfig.get_proxy("http://proxy.example.com:8080") == "http://proxy.example.com:8080"
    assert SDKConfig.get_proxy({"http": "http://proxy.example.com:8080"}) == {"http": "http://proxy.example.com:8080"}


def test_get_proxy_from_env():
    """Test getting proxy from environment variable."""
    with patch.dict(os.environ, {"SIDESHIFT_PROXY": "http://proxy.example.com:8080"}):
        assert SDKConfig.get_proxy() == "http://proxy.example.com:8080"


def test_get_proxy_from_http_proxy_env():
    """Test getting proxy from HTTP_PROXY environment variable."""
    with patch.dict(os.environ, {"HTTP_PROXY": "http://proxy.example.com:8080"}):
        result = SDKConfig.get_proxy()
        assert isinstance(result, dict)
        assert result["http"] == "http://proxy.example.com:8080"


def test_get_proxy_from_https_proxy_env():
    """Test getting proxy from HTTPS_PROXY environment variable."""
    with patch.dict(os.environ, {"HTTPS_PROXY": "https://proxy.example.com:8080"}):
        result = SDKConfig.get_proxy()
        assert isinstance(result, dict)
        assert result["https"] == "https://proxy.example.com:8080"


def test_get_proxy_default():
    """Test getting default proxy when nothing provided."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("SIDESHIFT_PROXY", None)
        os.environ.pop("HTTP_PROXY", None)
        os.environ.pop("HTTPS_PROXY", None)
        os.environ.pop("http_proxy", None)
        os.environ.pop("https_proxy", None)
        assert SDKConfig.get_proxy() is None


def test_client_uses_config_proxy():
    """Test that client uses configurable proxy."""
    client = SideShiftClient(secret="test-secret", proxy="http://proxy.example.com:8080")
    assert client.proxy == "http://proxy.example.com:8080"


def test_client_uses_env_proxy():
    """Test that client uses proxy from environment variable."""
    with patch.dict(os.environ, {"SIDESHIFT_PROXY": "http://proxy.example.com:8080"}):
        client = SideShiftClient(secret="test-secret")
        assert client.proxy == "http://proxy.example.com:8080"


@pytest.mark.asyncio
async def test_async_client_uses_config_proxy():
    """Test that async client uses configurable proxy."""
    async with AsyncSideShiftClient(secret="test-secret", proxy="http://proxy.example.com:8080") as client:
        assert client.proxy == "http://proxy.example.com:8080"


def test_client_uses_config_max_retries():
    """Test that client uses configurable max retries."""
    client = SideShiftClient(secret="test-secret", max_retries=5)
    assert client.max_retries == 5


def test_client_uses_env_max_retries():
    """Test that client uses max retries from environment variable."""
    with patch.dict(os.environ, {"SIDESHIFT_MAX_RETRIES": "7"}):
        client = SideShiftClient(secret="test-secret")
        assert client.max_retries == 7


    @pytest.mark.asyncio
    async def test_async_client_uses_config_max_retries():
        """Test that async client uses configurable max retries."""
        async with AsyncSideShiftClient(secret="test-secret", max_retries=5) as client:
            assert client.max_retries == 5


def test_get_api_version_default():
    """Test that get_api_version returns default version."""
    assert SDKConfig.get_api_version() == "v2"


def test_get_api_version_from_provided():
    """Test that get_api_version uses provided value."""
    assert SDKConfig.get_api_version(provided="v2") == "v2"


def test_get_api_version_from_env():
    """Test that get_api_version uses environment variable."""
    with patch.dict(os.environ, {"SIDESHIFT_API_VERSION": "v2"}):
        assert SDKConfig.get_api_version() == "v2"


def test_get_api_version_provided_overrides_env():
    """Test that provided value overrides environment variable."""
    with patch.dict(os.environ, {"SIDESHIFT_API_VERSION": "v2"}):
        assert SDKConfig.get_api_version(provided="v2") == "v2"


def test_get_api_version_unsupported():
    """Test that get_api_version raises ValueError for unsupported version."""
    with pytest.raises(ValueError, match="Unsupported API version"):
        SDKConfig.get_api_version(provided="v1")


def test_get_api_version_unsupported_from_env():
    """Test that get_api_version raises ValueError for unsupported version from env."""
    with patch.dict(os.environ, {"SIDESHIFT_API_VERSION": "v1"}):
        with pytest.raises(ValueError, match="Unsupported API version"):
            SDKConfig.get_api_version()


def test_get_base_url_from_api_version():
    """Test that get_base_url constructs URL from API version."""
    url = SDKConfig.get_base_url(api_version="v2")
    assert url == "https://sideshift.ai/api/v2"


def test_get_base_url_provided_overrides_api_version():
    """Test that provided base_url overrides api_version."""
    custom_url = "https://custom.example.com/api"
    url = SDKConfig.get_base_url(provided=custom_url, api_version="v2")
    assert url == custom_url


def test_client_uses_api_version():
    """Test that client uses API version to construct base URL."""
    client = SideShiftClient(secret="test-secret", api_version="v2")
    assert client.api_version == "v2"
    assert client.base_url == "https://sideshift.ai/api/v2"


def test_client_uses_env_api_version():
    """Test that client uses API version from environment variable."""
    with patch.dict(os.environ, {"SIDESHIFT_API_VERSION": "v2"}):
        client = SideShiftClient(secret="test-secret")
        assert client.api_version == "v2"
        assert client.base_url == "https://sideshift.ai/api/v2"


def test_client_base_url_overrides_api_version():
    """Test that base_url parameter overrides api_version."""
    custom_url = "https://custom.example.com/api"
    client = SideShiftClient(secret="test-secret", base_url=custom_url, api_version="v2")
    assert client.base_url == custom_url
    assert client.api_version == "v2"  # Still set, but base_url takes precedence


def test_client_unsupported_api_version():
    """Test that client raises ValueError for unsupported API version."""
    with pytest.raises(ValueError, match="Unsupported API version"):
        SideShiftClient(secret="test-secret", api_version="v1")


@pytest.mark.asyncio
async def test_async_client_uses_api_version():
    """Test that async client uses API version to construct base URL."""
    async with AsyncSideShiftClient(secret="test-secret", api_version="v2") as client:
        assert client.api_version == "v2"
        assert client.base_url == "https://sideshift.ai/api/v2"

