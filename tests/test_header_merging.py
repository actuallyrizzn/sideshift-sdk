"""Tests for header merging functionality."""

import logging
from unittest.mock import Mock, patch

import pytest
import requests

from sideshift_sdk.client import SideShiftClient
from sideshift_sdk.constants import (
    HEADER_ACCEPT,
    HEADER_CONTENT_TYPE,
    HEADER_REQUEST_ID,
    HEADER_USER_AGENT,
)


def test_merge_headers_protects_sdk_headers():
    """Test that SDK-managed headers are protected from user override."""
    client = SideShiftClient(secret="test-secret")
    
    sdk_headers = client._get_headers()
    user_headers = {
        HEADER_CONTENT_TYPE: "text/plain",  # Try to override
        HEADER_ACCEPT: "text/html",  # Try to override
        HEADER_USER_AGENT: "custom-agent",  # Try to override
        "Custom-Header": "custom-value",  # This should be allowed
    }
    
    merged = client._merge_headers(sdk_headers, user_headers)
    
    # SDK headers should be preserved
    assert merged[HEADER_CONTENT_TYPE] == sdk_headers[HEADER_CONTENT_TYPE]
    assert merged[HEADER_ACCEPT] == sdk_headers[HEADER_ACCEPT]
    assert merged[HEADER_USER_AGENT] == sdk_headers[HEADER_USER_AGENT]
    
    # Custom header should be included
    assert merged["Custom-Header"] == "custom-value"


def test_merge_headers_case_insensitive_protection():
    """Test that header protection works case-insensitively."""
    client = SideShiftClient(secret="test-secret")
    
    sdk_headers = client._get_headers()
    user_headers = {
        "content-type": "text/plain",  # Lowercase
        "ACCEPT": "text/html",  # Uppercase
        "User-Agent": "custom-agent",  # Mixed case
    }
    
    merged = client._merge_headers(sdk_headers, user_headers)
    
    # SDK headers should be preserved regardless of case
    assert merged[HEADER_CONTENT_TYPE] == sdk_headers[HEADER_CONTENT_TYPE]
    assert merged[HEADER_ACCEPT] == sdk_headers[HEADER_ACCEPT]
    assert merged[HEADER_USER_AGENT] == sdk_headers[HEADER_USER_AGENT]


def test_merge_headers_protects_request_id():
    """Test that X-Request-ID is protected from user override."""
    client = SideShiftClient(secret="test-secret")
    
    request_id = "sdk-request-id"
    sdk_headers = client._get_headers(request_id=request_id)
    user_headers = {
        HEADER_REQUEST_ID: "user-request-id",  # Try to override
    }
    
    merged = client._merge_headers(sdk_headers, user_headers)
    
    # SDK request ID should be preserved
    assert merged[HEADER_REQUEST_ID] == request_id


def test_merge_headers_logs_warning_when_protected_header_overridden():
    """Test that a warning is logged when user tries to override protected header."""
    client = SideShiftClient(secret="test-secret", enable_logging=True, log_level=logging.WARNING)
    
    sdk_headers = client._get_headers()
    user_headers = {
        HEADER_CONTENT_TYPE: "text/plain",
    }
    
    with patch.object(client._logger, "warning") as mock_warning:
        client._merge_headers(sdk_headers, user_headers)
        mock_warning.assert_called_once()
        assert "protected" in mock_warning.call_args[0][0].lower()


def test_merge_headers_allows_non_protected_headers():
    """Test that non-protected headers from user are included."""
    client = SideShiftClient(secret="test-secret")
    
    sdk_headers = client._get_headers()
    user_headers = {
        "X-Custom-Header": "custom-value",
        "Authorization": "Bearer token",
        "X-API-Key": "api-key",
    }
    
    merged = client._merge_headers(sdk_headers, user_headers)
    
    # All user headers should be included
    assert merged["X-Custom-Header"] == "custom-value"
    assert merged["Authorization"] == "Bearer token"
    assert merged["X-API-Key"] == "api-key"


def test_merge_headers_with_none():
    """Test that merging with None returns SDK headers unchanged."""
    client = SideShiftClient(secret="test-secret")
    
    sdk_headers = client._get_headers()
    merged = client._merge_headers(sdk_headers, None)
    
    assert merged == sdk_headers
    assert merged is not sdk_headers  # Should be a copy


def test_merge_headers_with_empty_dict():
    """Test that merging with empty dict returns SDK headers unchanged."""
    client = SideShiftClient(secret="test-secret")
    
    sdk_headers = client._get_headers()
    merged = client._merge_headers(sdk_headers, {})
    
    assert merged == sdk_headers
    assert merged is not sdk_headers  # Should be a copy


def test_request_uses_merged_headers():
    """Test that _request method uses merged headers correctly."""
    client = SideShiftClient(secret="test-secret")
    
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}
    mock_response.headers = {}
    
    user_headers = {
        HEADER_CONTENT_TYPE: "text/plain",  # Should be ignored
        "X-Custom-Header": "custom-value",  # Should be included
    }
    
    with patch.object(client._session, "request", return_value=mock_response) as mock_request:
        client._request("GET", "/test", headers=user_headers)
        
        # Verify request was made
        mock_request.assert_called_once()
        call_headers = mock_request.call_args[1]["headers"]
        
        # SDK headers should be preserved
        assert call_headers[HEADER_CONTENT_TYPE] != "text/plain"
        assert HEADER_CONTENT_TYPE in call_headers
        
        # Custom header should be included
        assert call_headers["X-Custom-Header"] == "custom-value"


def test_get_binary_uses_merged_headers():
    """Test that get_binary method uses merged headers correctly."""
    client = SideShiftClient(secret="test-secret")
    
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.content = b"binary data"
    mock_response.headers = {}
    
    user_headers = {
        HEADER_ACCEPT: "text/html",  # Should be ignored
        "X-Custom-Header": "custom-value",  # Should be included
    }
    
    with patch.object(client._session, "get", return_value=mock_response) as mock_get:
        client.get_binary("/test", headers=user_headers)
        
        # Verify request was made
        mock_get.assert_called_once()
        call_headers = mock_get.call_args[1]["headers"]
        
        # SDK headers should be preserved
        assert call_headers[HEADER_ACCEPT] != "text/html"
        assert HEADER_ACCEPT in call_headers
        
        # Custom header should be included
        assert call_headers["X-Custom-Header"] == "custom-value"

