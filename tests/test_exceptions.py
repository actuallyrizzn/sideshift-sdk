"""Tests for exception classes."""

from sideshift_sdk.exceptions import (
    SideShiftAPIError,
    SideShiftAuthenticationError,
    SideShiftException,
    SideShiftForbiddenError,
    SideShiftNetworkError,
    SideShiftNotFoundError,
    SideShiftRateLimitError,
)


def test_base_exception():
    """Test base SideShiftException."""
    exc = SideShiftException("Test error", status_code=400, response_data={"key": "value"})
    assert str(exc) == "Test error"
    assert exc.message == "Test error"
    assert exc.status_code == 400
    assert exc.response_data == {"key": "value"}


def test_api_error():
    """Test SideShiftAPIError."""
    exc = SideShiftAPIError("API error", status_code=500, response_data={"error": "server error"})
    assert exc.message == "API error"
    assert exc.status_code == 500
    assert exc.response_data == {"error": "server error"}


def test_authentication_error():
    """Test SideShiftAuthenticationError."""
    exc = SideShiftAuthenticationError("Auth failed", response_data={"error": "invalid key"})
    assert exc.message == "Auth failed"
    assert exc.status_code == 401
    assert exc.response_data == {"error": "invalid key"}

    # Test default message
    exc2 = SideShiftAuthenticationError()
    assert exc2.message == "Authentication failed"
    assert exc2.status_code == 401


def test_forbidden_error():
    """Test SideShiftForbiddenError."""
    exc = SideShiftForbiddenError("Forbidden", response_data={"error": "no access"})
    assert exc.message == "Forbidden"
    assert exc.status_code == 403
    assert exc.response_data == {"error": "no access"}

    # Test default message
    exc2 = SideShiftForbiddenError()
    assert exc2.message == "Access forbidden"
    assert exc2.status_code == 403


def test_not_found_error():
    """Test SideShiftNotFoundError."""
    exc = SideShiftNotFoundError("Not found", response_data={"error": "resource missing"})
    assert exc.message == "Not found"
    assert exc.status_code == 404
    assert exc.response_data == {"error": "resource missing"}

    # Test default message
    exc2 = SideShiftNotFoundError()
    assert exc2.message == "Resource not found"
    assert exc2.status_code == 404


def test_rate_limit_error():
    """Test SideShiftRateLimitError."""
    exc = SideShiftRateLimitError("Rate limited", response_data={"retry_after": 60})
    assert exc.message == "Rate limited"
    assert exc.status_code == 429
    assert exc.response_data == {"retry_after": 60}

    # Test default message
    exc2 = SideShiftRateLimitError()
    assert exc2.message == "Rate limit exceeded"
    assert exc2.status_code == 429


def test_network_error():
    """Test network error."""
    exc = SideShiftNetworkError("Network error occurred")
    assert exc.message == "Network error occurred"
    assert exc.status_code is None
    assert exc.response_data is None

    # Test default message
    exc2 = SideShiftNetworkError()
    assert exc2.message == "Network error"
    assert exc2.status_code is None
