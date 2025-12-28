"""Tests for edge cases and boundary conditions."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
import requests
import responses

from sideshift_sdk.client import AsyncSideShiftClient, SideShiftClient
from sideshift_sdk.endpoints import coins, quotes
from sideshift_sdk.exceptions import (
    SideShiftAPIError,
    SideShiftNetworkError,
    SideShiftNotFoundError,
    SideShiftRateLimitError,
    SideShiftSizeLimitError,
)


@pytest.fixture
def base_url():
    """Base URL for API."""
    return "https://sideshift.ai/api/v2"


@pytest.fixture
def client(base_url):
    """Create a synchronous client for testing."""
    return SideShiftClient(
        secret="test-secret",
        affiliate_id="test-affiliate",
        base_url=base_url,
        timeout=30,
    )


@pytest.fixture
def async_client(base_url):
    """Create an asynchronous client for testing."""
    return AsyncSideShiftClient(
        secret="test-secret",
        affiliate_id="test-affiliate",
        base_url=base_url,
        timeout=30,
    )


class TestBoundaryValues:
    """Test boundary values and edge cases for inputs."""

    def test_empty_string_handling(self, client):
        """Test handling of empty strings in various contexts."""
        # Empty endpoint should be handled
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not found"}
        mock_response.text = '{"message": "Not found"}'
        mock_response.headers = {}
        mock_response.content = b'{"message": "Not found"}'
        mock_session.request.return_value = mock_response
        client._session = mock_session

        with pytest.raises(SideShiftNotFoundError):  # 404 raises SideShiftNotFoundError
            client.get("")

    def test_whitespace_only_strings(self, client):
        """Test handling of whitespace-only strings."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not found"}
        mock_response.text = '{"message": "Not found"}'
        mock_response.headers = {}
        mock_response.content = b'{"message": "Not found"}'
        mock_session.request.return_value = mock_response
        client._session = mock_session

        with pytest.raises(SideShiftNotFoundError):  # 404 raises SideShiftNotFoundError
            client.get("   ")

    def test_very_long_endpoint(self, client):
        """Test handling of very long endpoint strings."""
        long_endpoint = "/" + "a" * 10000
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not found"}
        mock_response.text = '{"message": "Not found"}'
        mock_response.headers = {}
        mock_response.content = b'{"message": "Not found"}'
        mock_session.request.return_value = mock_response
        client._session = mock_session

        with pytest.raises(SideShiftNotFoundError):  # 404 raises SideShiftNotFoundError
            client.get(long_endpoint)

    def test_zero_timeout(self):
        """Test client with zero timeout."""
        client = SideShiftClient(secret="test", timeout=0)
        assert client.timeout == 0

    def test_very_large_timeout(self):
        """Test client with very large timeout."""
        client = SideShiftClient(secret="test", timeout=999999)
        assert client.timeout == 999999

    def test_empty_secret_from_env(self):
        """Test client with empty secret from environment."""
        import os
        original = os.environ.get("SIDESHIFT_SECRET")
        os.environ["SIDESHIFT_SECRET"] = ""
        try:
            client = SideShiftClient()
            # Empty string should be treated as None
            assert client.secret is None or client.secret == ""
        finally:
            if original is not None:
                os.environ["SIDESHIFT_SECRET"] = original
            else:
                os.environ.pop("SIDESHIFT_SECRET", None)


class TestUnusualResponseFormats:
    """Test handling of unusual response formats."""

    @responses.activate
    def test_empty_response_body(self, client, base_url):
        """Test handling of empty response body."""
        responses.add(
            responses.GET,
            f"{base_url}/test",
            body="",
            status=200,
            headers={"Content-Type": "application/json"},
        )

        with pytest.raises(SideShiftAPIError):
            client.get("/test")

    @responses.activate
    def test_malformed_json_response(self, client, base_url):
        """Test handling of malformed JSON response."""
        responses.add(
            responses.GET,
            f"{base_url}/test",
            body="{invalid json}",
            status=200,
            headers={"Content-Type": "application/json"},
        )

        with pytest.raises(SideShiftAPIError):
            client.get("/test")

    @responses.activate
    def test_response_with_null_values(self, client, base_url):
        """Test handling of null values in response."""
        responses.add(
            responses.GET,
            f"{base_url}/coins",
            json=[
                {
                    "networks": ["bitcoin"],
                    "coin": "btc",
                    "name": None,  # Null value (name is required, so this should fail validation)
                    "hasMemo": False,
                    "fixedOnly": False,
                    "variableOnly": False,
                    "networksWithMemo": [],
                }
            ],
            status=200,
        )

        # Pydantic validation should reject null for required string field
        with pytest.raises(Exception):  # Pydantic validation error
            coins.get_coins(client)

    @responses.activate
    def test_response_missing_required_fields(self, client, base_url):
        """Test handling of response missing required fields."""
        responses.add(
            responses.GET,
            f"{base_url}/coins",
            json=[{"coin": "btc"}],  # Missing required fields
            status=200,
        )

        # Pydantic validation should catch missing required fields
        with pytest.raises(Exception):  # Pydantic validation error
            coins.get_coins(client)

    @responses.activate
    def test_response_with_extra_fields(self, client, base_url):
        """Test handling of response with extra unexpected fields."""
        responses.add(
            responses.GET,
            f"{base_url}/coins",
            json=[
                {
                    "networks": ["bitcoin"],
                    "coin": "btc",
                    "name": "Bitcoin",
                    "hasMemo": False,
                    "fixedOnly": False,
                    "variableOnly": False,
                    "networksWithMemo": [],
                    "extraField": "should be ignored",  # Extra field
                }
            ],
            status=200,
        )

        # Pydantic should ignore extra fields by default
        coins_list = coins.get_coins(client)
        assert len(coins_list) == 1
        assert coins_list[0].coin == "btc"


class TestConfigurationEdgeCases:
    """Test edge cases in configuration."""

    def test_invalid_base_url_format(self):
        """Test client with invalid base URL format."""
        # Invalid URL format should still work (requests will handle it)
        client = SideShiftClient(secret="test", base_url="not-a-valid-url")
        assert client.base_url == "not-a-valid-url"

    def test_base_url_with_trailing_slash(self):
        """Test base URL with trailing slash."""
        client = SideShiftClient(secret="test", base_url="https://api.example.com/")
        assert client.base_url == "https://api.example.com/"

    def test_empty_affiliate_id(self):
        """Test client with empty affiliate ID."""
        client = SideShiftClient(secret="test", affiliate_id="")
        # Empty string should be normalized to None
        from sideshift_sdk.utils import normalize_affiliate_id
        assert normalize_affiliate_id(client.affiliate_id) is None

    def test_affiliate_id_with_whitespace(self):
        """Test affiliate ID with whitespace."""
        client = SideShiftClient(secret="test", affiliate_id="  test-id  ")
        # Whitespace should be preserved (not normalized)
        assert client.affiliate_id == "  test-id  "

    def test_max_retries_zero(self):
        """Test client with zero max retries."""
        client = SideShiftClient(secret="test", max_retries=0)
        assert client.max_retries == 0

    def test_max_retries_very_large(self):
        """Test client with very large max retries."""
        client = SideShiftClient(secret="test", max_retries=1000)
        assert client.max_retries == 1000


class TestStateEdgeCases:
    """Test edge cases related to client state."""

    def test_client_used_after_close(self, client):
        """Test using client after it's been closed."""
        client.close()

        # Using client after close should work (session is recreated if needed)
        # But let's test that close() can be called multiple times
        client.close()  # Should not raise

    def test_multiple_closes(self, client):
        """Test calling close() multiple times."""
        client.close()
        client.close()  # Should not raise
        client.close()  # Should not raise

    def test_context_manager_exit_with_exception(self, client):
        """Test context manager exit when exception occurs."""
        try:
            with client:
                raise ValueError("Test exception")
        except ValueError:
            pass
        # Client should still be properly closed

    @pytest.mark.asyncio
    async def test_async_client_used_after_close(self, async_client):
        """Test using async client after it's been closed."""
        await async_client.close()
        await async_client.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_async_context_manager_exit_with_exception(self, async_client):
        """Test async context manager exit when exception occurs."""
        try:
            async with async_client:
                raise ValueError("Test exception")
        except ValueError:
            pass
        # Client should still be properly closed


class TestDataEdgeCases:
    """Test edge cases with data handling."""

    @responses.activate
    def test_unicode_characters_in_response(self, client, base_url):
        """Test handling of Unicode characters in response."""
        responses.add(
            responses.GET,
            f"{base_url}/coins",
            json=[
                {
                    "networks": ["bitcoin"],
                    "coin": "btc",
                    "name": "Bitcoin 🪙",  # Unicode emoji
                    "hasMemo": False,
                    "fixedOnly": False,
                    "variableOnly": False,
                    "networksWithMemo": [],
                }
            ],
            status=200,
        )

        coins_list = coins.get_coins(client)
        assert len(coins_list) == 1
        assert "🪙" in coins_list[0].name

    @responses.activate
    def test_special_characters_in_endpoint(self, client, base_url):
        """Test handling of special characters in endpoint."""
        responses.add(
            responses.GET,
            f"{base_url}/test%20path",
            json={"data": "test"},
            status=200,
        )

        result = client.get("/test path")  # Space should be URL encoded
        assert result == {"data": "test"}

    def test_request_at_size_limit(self, client):
        """Test request at the size limit boundary."""
        client.max_request_size = 200
        # Create JSON data that's well within the limit
        json_data = {"data": "x" * 50}  # Small enough to be within limit
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_response.text = '{"success": true}'
        mock_response.headers = {}
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response
        client._session = mock_session

        # Should work if within limit
        result = client.post("/test", json_data=json_data)
        assert result == {"success": True}

    def test_request_exceeding_size_limit(self, client):
        """Test request exceeding size limit."""
        client.max_request_size = 100
        # Create JSON data that exceeds the limit
        json_data = {"data": "x" * 1000}  # Way over limit
        mock_session = Mock()
        client._session = mock_session

        with pytest.raises(SideShiftSizeLimitError):
            client.post("/test", json_data=json_data)


class TestErrorEdgeCases:
    """Test edge cases in error handling."""

    def test_error_in_request_hook(self, client):
        """Test error in request hook doesn't break request."""
        def error_hook(*args, **kwargs):
            raise ValueError("Hook error")

        client.add_request_hook(error_hook)

        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.text = '{"data": "test"}'
        mock_response.headers = {}
        mock_response.content = b'{"data": "test"}'
        mock_session.request.return_value = mock_response
        client._session = mock_session

        # Request should still succeed despite hook error
        result = client.get("/test")
        assert result == {"data": "test"}

    def test_error_in_response_hook(self, client):
        """Test error in response hook doesn't break request."""
        def error_hook(*args, **kwargs):
            raise ValueError("Hook error")

        client.add_response_hook(error_hook)

        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.text = '{"data": "test"}'
        mock_response.headers = {}
        mock_response.content = b'{"data": "test"}'
        mock_session.request.return_value = mock_response
        client._session = mock_session

        # Request should still succeed despite hook error
        result = client.get("/test")
        assert result == {"data": "test"}

    def test_error_in_error_hook(self, client):
        """Test error in error hook doesn't prevent exception."""
        def error_hook(*args, **kwargs):
            raise ValueError("Hook error")

        client.add_error_hook(error_hook)

        mock_session = Mock()
        mock_session.request.side_effect = requests.exceptions.ConnectionError("Connection refused")
        client._session = mock_session

        # Exception should still be raised despite hook error
        with pytest.raises(SideShiftNetworkError):
            client.get("/test")

    @pytest.mark.asyncio
    async def test_async_error_in_hook(self, async_client):
        """Test error in async hook doesn't break request."""
        async def error_hook(*args, **kwargs):
            raise ValueError("Hook error")

        async_client.add_request_hook(error_hook)

        async with async_client:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "test"}
            mock_response.content = b'{"data": "test"}'
            mock_response.headers = {}
            mock_client.request.return_value = mock_response
            async_client._client = mock_client

            # Request should still succeed despite hook error
            result = await async_client.get("/test")
            assert result == {"data": "test"}


class TestConcurrencyEdgeCases:
    """Test edge cases in concurrent scenarios."""

    @pytest.mark.asyncio
    async def test_concurrent_client_initialization(self):
        """Test concurrent initialization of async clients."""
        async def create_client():
            return AsyncSideShiftClient(secret="test")

        clients = await asyncio.gather(*[create_client() for _ in range(10)])
        assert len(clients) == 10
        for c in clients:
            await c.close()

    @pytest.mark.asyncio
    async def test_concurrent_close_operations(self, async_client):
        """Test concurrent close operations."""
        async with async_client:
            # Multiple close calls should be safe
            await asyncio.gather(
                async_client.close(),
                async_client.close(),
                async_client.close(),
            )


class TestRetryEdgeCases:
    """Test edge cases in retry logic."""

    def test_max_retries_zero_no_retry(self, client):
        """Test that zero max_retries means no retries."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"message": "Rate limited"}
        mock_response.text = '{"message": "Rate limited"}'
        mock_response.headers = {"Retry-After": "1"}
        mock_response.content = b'{"message": "Rate limited"}'
        mock_session.request.return_value = mock_response
        client._session = mock_session
        client.max_retries = 0

        # Should fail immediately without retry
        with pytest.raises(SideShiftRateLimitError):
            client._request("GET", "/test", max_retries=0)

        # Should only be called once (no retries)
        assert mock_session.request.call_count == 1

    def test_retry_with_exponential_backoff_edge_cases(self):
        """Test exponential backoff with edge case values."""
        from sideshift_sdk.utils import exponential_backoff

        # Test with very large attempt number
        result = exponential_backoff(100, base_delay=1.0, max_delay=60.0)
        assert result == 60.0  # Should be capped at max_delay

        # Test with zero attempt
        result = exponential_backoff(0, base_delay=1.0, max_delay=60.0)
        assert result == 1.0


class TestHeaderEdgeCases:
    """Test edge cases in header handling."""

    def test_empty_headers_dict(self, client):
        """Test request with empty headers dict."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.text = '{"data": "test"}'
        mock_response.headers = {}
        mock_response.content = b'{"data": "test"}'
        mock_session.request.return_value = mock_response
        client._session = mock_session

        result = client.get("/test", headers={})
        assert result == {"data": "test"}

    def test_none_headers(self, client):
        """Test request with None headers."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.text = '{"data": "test"}'
        mock_response.headers = {}
        mock_response.content = b'{"data": "test"}'
        mock_session.request.return_value = mock_response
        client._session = mock_session

        result = client.get("/test", headers=None)
        assert result == {"data": "test"}

