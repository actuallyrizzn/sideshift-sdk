"""Tests for middleware hooks functionality."""

import pytest

from sideshift_sdk import SideShiftClient, AsyncSideShiftClient
from sideshift_sdk.exceptions import SideShiftAPIError


def test_add_request_hook():
    """Test adding a request hook."""
    client = SideShiftClient(secret="test-secret")
    
    request_calls = []
    
    def request_hook(method, endpoint, params, json_data, headers):
        request_calls.append((method, endpoint))
    
    client.add_request_hook(request_hook)
    assert len(client._request_hooks) == 1


def test_add_response_hook():
    """Test adding a response hook."""
    client = SideShiftClient(secret="test-secret")
    
    response_calls = []
    
    def response_hook(method, endpoint, response_data):
        response_calls.append((method, endpoint))
    
    client.add_response_hook(response_hook)
    assert len(client._response_hooks) == 1


def test_add_error_hook():
    """Test adding an error hook."""
    client = SideShiftClient(secret="test-secret")
    
    error_calls = []
    
    def error_hook(exception, method, endpoint):
        error_calls.append((method, endpoint))
    
    client.add_error_hook(error_hook)
    assert len(client._error_hooks) == 1


def test_remove_hooks():
    """Test removing hooks."""
    client = SideShiftClient(secret="test-secret")
    
    def request_hook(method, endpoint, params, json_data, headers):
        pass
    
    def response_hook(method, endpoint, response_data):
        pass
    
    def error_hook(exception, method, endpoint):
        pass
    
    client.add_request_hook(request_hook)
    client.add_response_hook(response_hook)
    client.add_error_hook(error_hook)
    
    assert len(client._request_hooks) == 1
    assert len(client._response_hooks) == 1
    assert len(client._error_hooks) == 1
    
    client.remove_request_hook(request_hook)
    client.remove_response_hook(response_hook)
    client.remove_error_hook(error_hook)
    
    assert len(client._request_hooks) == 0
    assert len(client._response_hooks) == 0
    assert len(client._error_hooks) == 0


def test_request_hook_called():
    """Test that request hooks are called."""
    client = SideShiftClient(secret="test-secret")
    
    request_calls = []
    
    def request_hook(method, endpoint, params, json_data, headers):
        request_calls.append((method, endpoint))
    
    client.add_request_hook(request_hook)
    
    # Mock the session to avoid actual network calls
    from unittest.mock import Mock, patch
    
    with patch.object(client._session, "request") as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_request.return_value = mock_response
        
        client.get("/test-endpoint")
        
        assert len(request_calls) == 1
        assert request_calls[0] == ("GET", "/test-endpoint")


def test_response_hook_called():
    """Test that response hooks are called."""
    client = SideShiftClient(secret="test-secret")
    
    response_calls = []
    
    def response_hook(method, endpoint, response_data):
        response_calls.append((method, endpoint, response_data))
    
    client.add_response_hook(response_hook)
    
    # Mock the session to avoid actual network calls
    from unittest.mock import Mock, patch
    
    with patch.object(client._session, "request") as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_request.return_value = mock_response
        
        client.get("/test-endpoint")
        
        assert len(response_calls) == 1
        assert response_calls[0][0] == "GET"
        assert response_calls[0][1] == "/test-endpoint"
        assert response_calls[0][2] == {"test": "data"}


def test_error_hook_called():
    """Test that error hooks are called."""
    client = SideShiftClient(secret="test-secret")
    
    error_calls = []
    
    def error_hook(exception, method, endpoint):
        error_calls.append((type(exception).__name__, method, endpoint))
    
    client.add_error_hook(error_hook)
    
    # Mock the session to return 401 error
    from unittest.mock import Mock, patch
    
    with patch.object(client._session, "request") as mock_request:
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Authentication failed"}
        mock_request.return_value = mock_response
        
        with pytest.raises(Exception):
            client.get("/test-endpoint", require_auth=True)
        
        assert len(error_calls) == 1
        assert error_calls[0][1] == "GET"
        assert error_calls[0][2] == "/test-endpoint"


@pytest.mark.asyncio
async def test_async_hooks():
    """Test async hooks with async client."""
    async with AsyncSideShiftClient(secret="test-secret") as client:
        request_calls = []
        response_calls = []
        
        async def async_request_hook(method, endpoint, params, json_data, headers):
            request_calls.append((method, endpoint))
        
        async def async_response_hook(method, endpoint, response_data):
            response_calls.append((method, endpoint))
        
        client.add_request_hook(async_request_hook)
        client.add_response_hook(async_response_hook)
        
        # Mock the httpx client
        from unittest.mock import AsyncMock, Mock, patch
        
        with patch.object(client, "_get_client") as mock_get_client:
            mock_httpx_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"test": "data"}
            mock_httpx_client.request.return_value = mock_response
            mock_get_client.return_value = mock_httpx_client
            
            await client.get("/test-endpoint")
            
            assert len(request_calls) == 1
            assert len(response_calls) == 1

