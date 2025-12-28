"""Tests for utility functions."""

import time
from unittest.mock import patch

import pytest

from sideshift_sdk.utils import (
    build_coin_network,
    exponential_backoff,
    handle_rate_limit,
    validate_non_empty_string,
    validate_positive_amount,
)


def test_exponential_backoff():
    """Test exponential backoff calculation."""
    # Test base case
    assert exponential_backoff(0) == 1.0
    assert exponential_backoff(1) == 2.0
    assert exponential_backoff(2) == 4.0
    assert exponential_backoff(3) == 8.0

    # Test with custom base delay
    assert exponential_backoff(0, base_delay=2.0) == 2.0
    assert exponential_backoff(1, base_delay=2.0) == 4.0

    # Test max delay cap
    assert exponential_backoff(10, base_delay=1.0, max_delay=60.0) == 60.0
    assert exponential_backoff(100, base_delay=1.0, max_delay=60.0) == 60.0

    # Test that it doesn't exceed max
    result = exponential_backoff(20, base_delay=1.0, max_delay=60.0)
    assert result == 60.0


@patch("sideshift_sdk.utils.time.sleep")
def test_handle_rate_limit(mock_sleep):
    """Test rate limit handling."""
    # Test with retry_after
    handle_rate_limit(retry_after=30)
    mock_sleep.assert_called_once_with(30)

    # Test without retry_after (default 60)
    mock_sleep.reset_mock()
    handle_rate_limit()
    mock_sleep.assert_called_once_with(60)


def test_build_coin_network():
    """Test coin-network identifier building."""
    # Test with network
    assert build_coin_network("btc", "mainnet") == "btc-mainnet"
    assert build_coin_network("eth", "ethereum") == "eth-ethereum"

    # Test without network
    assert build_coin_network("btc") == "btc"
    assert build_coin_network("eth", None) == "eth"

    # Test with empty network
    assert build_coin_network("btc", "") == "btc-"


def test_validate_non_empty_string():
    """Test validate_non_empty_string function."""
    # Valid cases
    validate_non_empty_string("test", "param")
    validate_non_empty_string("  test  ", "param")  # Whitespace is OK, just not empty

    # Invalid cases
    with pytest.raises(ValueError, match="cannot be None"):
        validate_non_empty_string(None, "param")

    with pytest.raises(ValueError, match="cannot be empty"):
        validate_non_empty_string("", "param")

    with pytest.raises(ValueError, match="cannot be empty"):
        validate_non_empty_string("   ", "param")

    with pytest.raises(TypeError, match="must be a string"):
        validate_non_empty_string(123, "param")


def test_validate_positive_amount():
    """Test validate_positive_amount function."""
    # Valid cases
    validate_positive_amount("1.0", "amount")
    validate_positive_amount("0.001", "amount")
    validate_positive_amount("100", "amount")
    validate_positive_amount(None, "amount")  # None is allowed

    # Invalid cases
    with pytest.raises(ValueError, match="cannot be empty"):
        validate_positive_amount("", "amount")

    with pytest.raises(ValueError, match="cannot be empty"):
        validate_positive_amount("   ", "amount")

    with pytest.raises(ValueError, match="must be positive"):
        validate_positive_amount("0", "amount")

    with pytest.raises(ValueError, match="must be positive"):
        validate_positive_amount("-1", "amount")

    with pytest.raises(ValueError, match="must be a valid number"):
        validate_positive_amount("not a number", "amount")

    with pytest.raises(TypeError, match="must be a string"):
        validate_positive_amount(123, "amount")
