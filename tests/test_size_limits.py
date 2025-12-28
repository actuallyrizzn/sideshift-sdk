"""Tests for request/response size limits."""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
import requests
import httpx

from sideshift_sdk.client import AsyncSideShiftClient, SideShiftClient
from sideshift_sdk.exceptions import SideShiftSizeLimitError
from sideshift_sdk.config import SDKConfig


def test_client_initialization_with_size_limits():
    """Test client initialization with size limits."""
    client = SideShiftClient(
        secret="test-secret",
        max_request_size=5 * 1024 * 1024,  # 5MB
        max_response_size=20 * 1024 * 1024,  # 20MB
    )
    assert client.max_request_size == 5 * 1024 * 1024
    assert client.max_response_size == 20 * 1024 * 1024


def test_client_uses_default_size_limits():
    """Test client uses default size limits when not specified."""
    client = SideShiftClient(secret="test-secret")
    assert client.max_request_size == SDKConfig.DEFAULT_MAX_REQUEST_SIZE
    assert client.max_response_size == SDKConfig.DEFAULT_MAX_RESPONSE_SIZE


def test_request_size_validation_exceeds_limit():
    """Test that request size validation raises error when limit is exceeded."""
    client = SideShiftClient(secret="test-secret", max_request_size=100)  # 100 bytes limit
    
    # Create a JSON payload that exceeds 100 bytes
    large_payload = {"data": "x" * 200}  # This will be > 100 bytes when serialized
    
    with pytest.raises(SideShiftSizeLimitError) as exc_info:
        client._request(
            "POST",
            "/test",
            json_data=large_payload,
        )
    
    assert "exceeds maximum allowed size" in str(exc_info.value)
    assert exc_info.value.method == "POST"
    assert exc_info.value.endpoint == "/test"


def test_request_size_validation_within_limit():
    """Test that request size validation passes when within limit."""
    client = SideShiftClient(secret="test-secret", max_request_size=10 * 1024 * 1024)  # 10MB limit
    
    # Create a small JSON payload
    small_payload = {"data": "test"}
    
    # Mock the session to avoid actual HTTP request
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}
    mock_response.headers = {}
    mock_response.content = b'{"success": true}'  # Set content to avoid len() error
    
    with patch.object(client._session, "request", return_value=mock_response):
        result = client._request("POST", "/test", json_data=small_payload)
        assert result == {"success": True}


def test_response_size_validation_content_length_exceeds_limit():
    """Test that response size validation raises error when Content-Length exceeds limit."""
    client = SideShiftClient(secret="test-secret", max_response_size=100)  # 100 bytes limit
    
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.headers = {"Content-Length": "200"}  # Exceeds limit
    mock_response.json.return_value = {"data": "test"}
    
    with patch.object(client._session, "request", return_value=mock_response):
        with pytest.raises(SideShiftSizeLimitError) as exc_info:
            client._request("GET", "/test")
        
        assert "exceeds maximum allowed size" in str(exc_info.value)
        assert exc_info.value.method == "GET"
        assert exc_info.value.endpoint == "/test"


def test_response_size_validation_content_length_within_limit():
    """Test that response size validation passes when Content-Length is within limit."""
    client = SideShiftClient(secret="test-secret", max_response_size=10 * 1024 * 1024)  # 10MB limit
    
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.headers = {"Content-Length": "100"}  # Within limit
    mock_response.json.return_value = {"data": "test"}
    
    with patch.object(client._session, "request", return_value=mock_response):
        result = client._request("GET", "/test")
        assert result == {"data": "test"}


def test_response_size_validation_no_content_length():
    """Test that response size validation checks actual content when Content-Length is missing."""
    client = SideShiftClient(secret="test-secret", max_response_size=100)  # 100 bytes limit
    
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.headers = {}  # No Content-Length
    mock_response.content = b"x" * 200  # 200 bytes, exceeds limit
    mock_response.json.return_value = {"data": "test"}
    
    with patch.object(client._session, "request", return_value=mock_response):
        with pytest.raises(SideShiftSizeLimitError) as exc_info:
            client._request("GET", "/test")
        
        assert "exceeds maximum allowed size" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_client_request_size_validation():
    """Test async client request size validation."""
    client = AsyncSideShiftClient(secret="test-secret", max_request_size=100)  # 100 bytes limit
    
    large_payload = {"data": "x" * 200}  # Exceeds limit
    
    with pytest.raises(SideShiftSizeLimitError) as exc_info:
        await client._request("POST", "/test", json_data=large_payload)
    
    assert "exceeds maximum allowed size" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_client_response_size_validation():
    """Test async client response size validation."""
    client = AsyncSideShiftClient(secret="test-secret", max_response_size=100)  # 100 bytes limit
    
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.headers = {"Content-Length": "200"}  # Exceeds limit
    mock_response.json.return_value = {"data": "test"}
    
    mock_client = AsyncMock()
    mock_client.request = AsyncMock(return_value=mock_response)
    
    with patch.object(client, "_get_client", return_value=mock_client):
        with pytest.raises(SideShiftSizeLimitError) as exc_info:
            await client._request("GET", "/test")
        
        assert "exceeds maximum allowed size" in str(exc_info.value)


def test_config_get_max_request_size():
    """Test SDKConfig.get_max_request_size."""
    # Test with provided value
    assert SDKConfig.get_max_request_size(5 * 1024 * 1024) == 5 * 1024 * 1024
    
    # Test with default
    assert SDKConfig.get_max_request_size(None) == SDKConfig.DEFAULT_MAX_REQUEST_SIZE


def test_config_get_max_response_size():
    """Test SDKConfig.get_max_response_size."""
    # Test with provided value
    assert SDKConfig.get_max_response_size(20 * 1024 * 1024) == 20 * 1024 * 1024
    
    # Test with default
    assert SDKConfig.get_max_response_size(None) == SDKConfig.DEFAULT_MAX_RESPONSE_SIZE


def test_size_limit_error_attributes():
    """Test that SideShiftSizeLimitError has correct attributes."""
    error = SideShiftSizeLimitError(
        "Size limit exceeded",
        response_data={"size": 200, "max_size": 100},
        request_id="test-123",
        method="POST",
        endpoint="/test",
    )
    
    assert error.message == "Size limit exceeded"
    assert error.request_id == "test-123"
    assert error.method == "POST"
    assert error.endpoint == "/test"
    assert error.response_data == {"size": 200, "max_size": 100}

