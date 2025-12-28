"""Tests for request ID/correlation tracking."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
import requests

from sideshift_sdk.client import AsyncSideShiftClient, SideShiftClient
from sideshift_sdk.constants import HEADER_REQUEST_ID
from sideshift_sdk.exceptions import SideShiftAPIError, SideShiftNetworkError


@patch("sideshift_sdk.client.requests.Session")
def test_client_request_id_generated(mock_session_class):
    """Test that request ID is generated and included in headers."""
    mock_session = Mock()
    mock_session_class.return_value = mock_session

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_session.request.return_value = mock_response

    client = SideShiftClient(secret="test-secret")
    client.get("/test")

    # Verify request was made with X-Request-ID header
    call_args = mock_session.request.call_args
    assert call_args is not None
    headers = call_args.kwargs.get("headers", {})
    assert HEADER_REQUEST_ID in headers
    request_id = headers[HEADER_REQUEST_ID]
    assert isinstance(request_id, str)
    assert len(request_id) > 0  # UUID should be non-empty


@patch("sideshift_sdk.client.requests.Session")
def test_client_request_id_user_provided(mock_session_class):
    """Test that user-provided request ID takes precedence."""
    mock_session = Mock()
    mock_session_class.return_value = mock_session

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_session.request.return_value = mock_response

    client = SideShiftClient(secret="test-secret")
    custom_request_id = "custom-request-id-12345"
    client.get("/test", headers={HEADER_REQUEST_ID: custom_request_id})

    # Verify user-provided request ID was used
    call_args = mock_session.request.call_args
    assert call_args is not None
    headers = call_args.kwargs.get("headers", {})
    assert headers[HEADER_REQUEST_ID] == custom_request_id


@patch("sideshift_sdk.client.requests.Session")
def test_client_request_id_in_error_response(mock_session_class):
    """Test that request ID is included in error response_data."""
    mock_session = Mock()
    mock_session_class.return_value = mock_session

    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"message": "Bad Request"}
    mock_session.request.return_value = mock_response

    client = SideShiftClient(secret="test-secret")
    with pytest.raises(SideShiftAPIError) as exc_info:
        client.get("/test")

    # Verify request ID is in error response_data
    assert exc_info.value.response_data is not None
    assert "request_id" in exc_info.value.response_data
    request_id = exc_info.value.response_data["request_id"]
    assert isinstance(request_id, str)
    assert len(request_id) > 0


@patch("sideshift_sdk.client.requests.Session")
def test_client_request_id_in_network_error(mock_session_class):
    """Test that request ID is included in network error response_data."""
    mock_session = Mock()
    mock_session_class.return_value = mock_session

    mock_session.request.side_effect = requests.exceptions.ConnectionError("Connection refused")

    client = SideShiftClient(secret="test-secret")
    with pytest.raises(SideShiftNetworkError) as exc_info:
        client.get("/test")

    # Verify request ID is in error response_data
    assert exc_info.value.response_data is not None
    assert "request_id" in exc_info.value.response_data


@pytest.mark.asyncio
async def test_async_client_request_id_generated():
    """Test that async client generates request ID."""
    async with AsyncSideShiftClient(secret="test-secret") as client:
        with patch.object(client, "_get_client") as mock_get_client:
            mock_httpx_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "test"}
            mock_httpx_client.request.return_value = mock_response
            mock_get_client.return_value = mock_httpx_client

            await client.get("/test")

            # Verify request was made with X-Request-ID header
            call_args = mock_httpx_client.request.call_args
            assert call_args is not None
            headers = call_args.kwargs.get("headers", {})
            assert HEADER_REQUEST_ID in headers
            request_id = headers[HEADER_REQUEST_ID]
            assert isinstance(request_id, str)
            assert len(request_id) > 0

