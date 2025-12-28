"""Tests for client classes."""

import os
from unittest.mock import AsyncMock, Mock, patch

import pytest
import requests

from sideshift_sdk.client import AsyncSideShiftClient, SideShiftClient
from sideshift_sdk.constants import HEADER_REQUEST_ID
from sideshift_sdk.exceptions import (
    SideShiftAPIError,
    SideShiftAuthenticationError,
    SideShiftForbiddenError,
    SideShiftNetworkError,
    SideShiftNotFoundError,
    SideShiftRateLimitError,
)


def test_client_initialization():
    """Test client initialization."""
    client = SideShiftClient(secret="test-secret", affiliate_id="test-affiliate")
    assert client.secret == "test-secret"
    assert client.affiliate_id == "test-affiliate"


def test_client_initialization_from_env():
    """Test client initialization from environment variables."""
    with patch.dict(
        os.environ, {"SIDESHIFT_SECRET": "env-secret", "AFFILIATE_ID": "env-affiliate"}
    ):
        client = SideShiftClient()
        assert client.secret == "env-secret"
        assert client.affiliate_id == "env-affiliate"


def test_client_get_headers():
    """Test header generation."""
    client = SideShiftClient(secret="test-secret", user_ip="1.2.3.4")

    headers = client._get_headers(include_secret=True, include_user_ip=True)
    assert headers["x-sideshift-secret"] == "test-secret"
    assert headers["x-user-ip"] == "1.2.3.4"
    assert headers["Content-Type"] == "application/json"


def test_client_handle_response_success():
    """Test successful response handling."""
    client = SideShiftClient()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}

    result = client._handle_response(mock_response)
    assert result == {"data": "test"}


def test_client_handle_response_200_json_parse_error():
    """Test 200 response handling when JSON parsing fails."""
    client = SideShiftClient()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_response.text = "HTML error page"

    with pytest.raises(SideShiftAPIError) as exc_info:
        client._handle_response(mock_response)

    assert exc_info.value.status_code == 200
    assert "Failed to parse JSON" in exc_info.value.message
    assert "HTML error page" in exc_info.value.message


def test_client_handle_response_201_json_parse_error():
    """Test 201 response handling when JSON parsing fails."""
    client = SideShiftClient()
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.side_effect = TypeError("Not JSON")
    mock_response.text = "Plain text response"

    with pytest.raises(SideShiftAPIError) as exc_info:
        client._handle_response(mock_response)

    assert exc_info.value.status_code == 201
    assert "Failed to parse JSON" in exc_info.value.message


def test_client_handle_response_401():
    """Test 401 response handling."""
    client = SideShiftClient()
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"message": "Unauthorized"}

    with pytest.raises(SideShiftAuthenticationError) as exc_info:
        client._handle_response(mock_response)

    assert exc_info.value.status_code == 401


def test_client_handle_response_429():
    """Test 429 rate limit response handling."""
    client = SideShiftClient()
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.headers = {"Retry-After": "60"}
    mock_response.json.return_value = {"message": "Rate limit exceeded"}

    with pytest.raises(SideShiftRateLimitError) as exc_info:
        client._handle_response(mock_response)

    assert exc_info.value.status_code == 429


def test_client_handle_response_400():
    """Test 400 error response handling."""
    client = SideShiftClient()
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"message": "Bad request"}

    with pytest.raises(SideShiftAPIError) as exc_info:
        client._handle_response(mock_response)

    assert exc_info.value.status_code == 400
    assert "Bad request" in exc_info.value.message


@patch("sideshift_sdk.client.requests.Session")
def test_client_get_request(mock_session_class):
    """Test GET request."""
    mock_session = Mock()
    mock_session_class.return_value = mock_session

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_session.request.return_value = mock_response

    client = SideShiftClient(secret="test-secret")
    result = client.get("/test", require_auth=True)

    assert result == {"data": "test"}
    mock_session.request.assert_called_once()


@patch("sideshift_sdk.client.requests.Session")
def test_client_post_request(mock_session_class):
    """Test POST request."""
    mock_session = Mock()
    mock_session_class.return_value = mock_session

    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": "test-id"}
    mock_session.request.return_value = mock_response

    client = SideShiftClient(secret="test-secret")
    result = client.post("/test", json_data={"key": "value"}, require_auth=True)

    assert result == {"id": "test-id"}
    mock_session.request.assert_called_once()


def test_client_context_manager():
    """Test client as context manager."""
    with SideShiftClient(secret="test-secret") as client:
        assert client.secret == "test-secret"

    # Session should be closed (close() was called)
    # Note: requests.Session doesn't have a 'closed' attribute,
    # but close() is called in __exit__


def test_client_handle_response_204():
    """Test 204 No Content response handling."""
    client = SideShiftClient()
    mock_response = Mock()
    mock_response.status_code = 204

    result = client._handle_response(mock_response)
    assert result == {}


def test_client_handle_response_403():
    """Test 403 Forbidden response handling."""
    client = SideShiftClient()
    mock_response = Mock()
    mock_response.status_code = 403
    mock_response.json.return_value = {"message": "Forbidden"}

    with pytest.raises(SideShiftForbiddenError) as exc_info:
        client._handle_response(mock_response)

    assert exc_info.value.status_code == 403


def test_client_handle_response_404():
    """Test 404 Not Found response handling."""
    client = SideShiftClient()
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"message": "Not found"}

    with pytest.raises(SideShiftNotFoundError) as exc_info:
        client._handle_response(mock_response)

    assert exc_info.value.status_code == 404


def test_client_handle_response_500():
    """Test 500 Internal Server Error response handling."""
    client = SideShiftClient()
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"message": "Internal server error"}

    with pytest.raises(SideShiftAPIError) as exc_info:
        client._handle_response(mock_response)

    assert exc_info.value.status_code == 500


def test_client_handle_response_no_json():
    """Test response handling when JSON parsing fails."""
    client = SideShiftClient()
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_response.text = "Bad request text"

    with pytest.raises(SideShiftAPIError) as exc_info:
        client._handle_response(mock_response)

    assert exc_info.value.status_code == 400
    assert "Bad request text" in exc_info.value.message


def test_client_handle_response_no_text():
    """Test response handling when text is not available."""
    client = SideShiftClient()
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.side_effect = ValueError("Invalid JSON")
    del mock_response.text  # Remove text attribute

    with pytest.raises(SideShiftAPIError) as exc_info:
        client._handle_response(mock_response)


@patch("sideshift_sdk.client.requests.Session")
def test_client_rate_limit_retry(mock_session_class):
    """Test rate limit retry logic."""
    mock_session = Mock()
    mock_session_class.return_value = mock_session

    # First call returns 429, second returns 200
    rate_limit_response = Mock()
    rate_limit_response.status_code = 429
    rate_limit_response.headers = {"Retry-After": "1"}

    success_response = Mock()
    success_response.status_code = 200
    success_response.json.return_value = {"data": "success"}
    success_response.content = b'{"data": "success"}'
    success_response.headers = {}

    mock_session.request.side_effect = [
        rate_limit_response,
        success_response,
    ]

    client = SideShiftClient(secret="test-secret", max_retries=1)

    # Should retry and succeed
    result = client.get("/test")
    assert result == {"data": "success"}
    assert mock_session.request.call_count == 2


def test_client_retry_after_header_parsing():
    """Test that Retry-After header is parsed and used for retry delay."""
    client = SideShiftClient(secret="test-secret", max_retries=1, enable_logging=True)
    
    # Test integer format (seconds)
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.headers = {"Retry-After": "5"}
    mock_response.json.return_value = {"error": "Rate limited"}
    mock_response.text = '{"error": "Rate limited"}'
    mock_response.content = b'{"error": "Rate limited"}'
    
    # Should raise SideShiftRateLimitError
    with pytest.raises(SideShiftRateLimitError) as exc_info:
        client._handle_response(mock_response, method="GET", endpoint="/test")
    
    assert exc_info.value.response_data is not None
    assert exc_info.value.response_data.get("retry_after") == 5


def test_client_retry_after_header_used_in_retry():
    """Test that Retry-After header value is used for retry delay instead of exponential backoff."""
    import time
    from unittest.mock import patch
    
    client = SideShiftClient(secret="test-secret", max_retries=1, enable_logging=True)
    
    # First response: 429 with Retry-After: 2
    rate_limit_response = Mock()
    rate_limit_response.status_code = 429
    rate_limit_response.headers = {"Retry-After": "2"}
    rate_limit_response.json.return_value = {"error": "Rate limited"}
    rate_limit_response.text = '{"error": "Rate limited"}'
    rate_limit_response.content = b'{"error": "Rate limited"}'
    
    # Second response: 200 success
    success_response = Mock()
    success_response.status_code = 200
    success_response.json.return_value = {"data": "success"}
    success_response.content = b'{"data": "success"}'
    success_response.headers = {}
    
    mock_session = Mock()
    mock_session.request.side_effect = [rate_limit_response, success_response]
    client._session = mock_session
    
    # Mock time.sleep to verify the delay
    with patch("sideshift_sdk.client.time.sleep") as mock_sleep:
        result = client.get("/test")
        assert result == {"data": "success"}
        # Verify that sleep was called with the Retry-After value (2 seconds)
        assert mock_sleep.called
        # Check that the sleep time was approximately 2 seconds (from Retry-After)
        # It should be 2.0, not the exponential backoff value
        call_args = mock_sleep.call_args[0]
        assert call_args[0] == 2.0  # Should use Retry-After value


def test_client_close():
    """Test client close method."""
    client = SideShiftClient(secret="test-secret")
    client.close()
    # Should not raise


@pytest.mark.asyncio
async def test_async_client_post():
    """Test async POST request."""
    async with AsyncSideShiftClient(secret="test-secret") as client:
        with patch.object(client, "_get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": "test-id"}
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await client.post("/test", json_data={"key": "value"}, require_auth=True)
            assert result == {"id": "test-id"}


@pytest.mark.asyncio
async def test_async_client_close():
    """Test async client close method."""
    async with AsyncSideShiftClient(secret="test-secret") as client:
        await client._get_client()  # Create client
        await client.close()
        # Should not raise


@pytest.mark.asyncio
async def test_async_client_context_manager():
    """Test async client as context manager."""
    async with AsyncSideShiftClient(secret="test-secret") as client:
        assert client.secret == "test-secret"


@pytest.mark.asyncio
async def test_async_client_initialization():
    """Test async client initialization."""
    async with AsyncSideShiftClient(secret="test-secret", affiliate_id="test-affiliate") as client:
        assert client.secret == "test-secret"
        assert client.affiliate_id == "test-affiliate"


@pytest.mark.asyncio
async def test_async_client_get():
    """Test async GET request."""
    async with AsyncSideShiftClient(secret="test-secret") as client:
        with patch.object(client, "_get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "test"}
            # Note: The actual code uses client.request(), not client.get()
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await client.get("/test", require_auth=True)
            assert result == {"data": "test"}


def test_client_network_error_connection():
    """Test network error handling for connection errors."""
    client = SideShiftClient()
    mock_session = Mock()
    mock_session.request.side_effect = requests.exceptions.ConnectionError("Connection refused")
    client._session = mock_session

    with pytest.raises(SideShiftNetworkError) as exc_info:
        client.get("/test")

    assert "Network error" in exc_info.value.message
    # Check that exception chaining is preserved
    assert exc_info.value.__cause__ is not None
    assert isinstance(exc_info.value.__cause__, requests.exceptions.ConnectionError)


def test_client_network_error_timeout():
    """Test network error handling for timeout errors."""
    client = SideShiftClient(timeout=5)
    mock_session = Mock()
    mock_session.request.side_effect = requests.exceptions.Timeout("Request timed out")
    client._session = mock_session

    with pytest.raises(SideShiftNetworkError) as exc_info:
        client.get("/test")

    assert "timeout" in exc_info.value.message.lower()
    assert "5 seconds" in exc_info.value.message
    # Check that exception chaining is preserved
    assert exc_info.value.__cause__ is not None


@pytest.mark.asyncio
async def test_async_client_network_error():
    """Test async network error handling."""
    import httpx

    client = AsyncSideShiftClient()
    mock_client = AsyncMock()
    mock_client.request.side_effect = httpx.ConnectError("Connection refused")
    client._client = mock_client

    with pytest.raises(SideShiftNetworkError) as exc_info:
        await client._request("GET", "/test")

    assert "Network error" in exc_info.value.message
    # Check that exception chaining is preserved
    assert exc_info.value.__cause__ is not None


def test_client_validate_request_body_none():
    """Test that None request body passes validation."""
    client = SideShiftClient(secret="test-secret")
    
    # None should pass validation (no body)
    client._validate_request_body(None, "POST", "/test")


def test_client_validate_request_body_valid_dict():
    """Test that valid dictionary passes validation."""
    client = SideShiftClient(secret="test-secret")
    
    # Valid dict should pass validation
    valid_data = {"key": "value", "number": 123, "bool": True, "null": None, "list": [1, 2, 3]}
    client._validate_request_body(valid_data, "POST", "/test")


def test_client_validate_request_body_invalid_type():
    """Test that non-dict types raise SideShiftAPIError."""
    client = SideShiftClient(secret="test-secret")
    
    # String should raise error
    with pytest.raises(SideShiftAPIError) as exc_info:
        client._validate_request_body("not a dict", "POST", "/test")
    assert exc_info.value.status_code == 400
    assert "must be a dictionary" in exc_info.value.message
    
    # List should raise error
    with pytest.raises(SideShiftAPIError) as exc_info:
        client._validate_request_body(["not", "a", "dict"], "POST", "/test")
    assert exc_info.value.status_code == 400
    assert "must be a dictionary" in exc_info.value.message
    
    # Integer should raise error
    with pytest.raises(SideShiftAPIError) as exc_info:
        client._validate_request_body(123, "POST", "/test")
    assert exc_info.value.status_code == 400
    assert "must be a dictionary" in exc_info.value.message


def test_client_validate_request_body_non_serializable():
    """Test that non-JSON-serializable data raises SideShiftAPIError."""
    client = SideShiftClient(secret="test-secret")
    
    # Function is not JSON-serializable
    def some_function():
        pass
    
    with pytest.raises(SideShiftAPIError) as exc_info:
        client._validate_request_body({"func": some_function}, "POST", "/test")
    assert exc_info.value.status_code == 400
    assert "not JSON-serializable" in exc_info.value.message
    assert exc_info.value.__cause__ is not None  # Exception chaining
    
    # Class instance is not JSON-serializable
    class SomeClass:
        pass
    
    with pytest.raises(SideShiftAPIError) as exc_info:
        client._validate_request_body({"obj": SomeClass()}, "POST", "/test")
    assert exc_info.value.status_code == 400
    assert "not JSON-serializable" in exc_info.value.message


def test_client_validate_request_body_in_request():
    """Test that request body validation is called in _request method."""
    client = SideShiftClient(secret="test-secret")
    
    # Invalid type should be caught before making HTTP request
    with pytest.raises(SideShiftAPIError) as exc_info:
        client._request("POST", "/test", json_data="not a dict")
    assert exc_info.value.status_code == 400
    assert "must be a dictionary" in exc_info.value.message


@pytest.mark.asyncio
async def test_async_client_validate_request_body_in_request():
    """Test that request body validation is called in async _request method."""
    # Invalid type should be caught before making HTTP request (before _get_client is called)
    # So we don't need to mock anything or use context manager
    client = AsyncSideShiftClient(secret="test-secret")
    
    with pytest.raises(SideShiftAPIError) as exc_info:
        await client._request("POST", "/test", json_data="not a dict")
    assert exc_info.value.status_code == 400
    assert "must be a dictionary" in exc_info.value.message
    
    # Ensure client is properly closed if it was created
    if client._client is not None:
        await client.close()
