"""Utility functions for SideShift SDK."""

import time


def validate_non_empty_string(value: str | None, param_name: str) -> None:
    """Validate that a string parameter is not None and not empty.

    Args:
        value: The value to validate
        param_name: Name of the parameter for error messages

    Raises:
        ValueError: If value is None or empty string
    """
    if value is None:
        raise ValueError(f"{param_name} cannot be None")
    if not isinstance(value, str):
        raise TypeError(f"{param_name} must be a string, got {type(value).__name__}")
    if not value.strip():
        raise ValueError(f"{param_name} cannot be empty")


def validate_positive_amount(amount: str | None, param_name: str) -> None:
    """Validate that an amount string represents a positive number.

    Args:
        amount: The amount string to validate
        param_name: Name of the parameter for error messages

    Raises:
        ValueError: If amount is invalid or non-positive
    """
    if amount is None:
        return  # None is allowed for optional amounts
    if not isinstance(amount, str):
        raise TypeError(f"{param_name} must be a string, got {type(amount).__name__}")
    if not amount.strip():
        raise ValueError(f"{param_name} cannot be empty")
    try:
        amount_float = float(amount)
        if amount_float <= 0:
            raise ValueError(f"{param_name} must be positive, got {amount}")
    except ValueError as e:
        if "could not convert" in str(e).lower():
            raise ValueError(f"{param_name} must be a valid number, got {amount}") from e
        raise


def handle_rate_limit(retry_after: int | None = None) -> None:
    """Handle rate limit by waiting.

    Args:
        retry_after: Number of seconds to wait (from Retry-After header)
    """
    wait_time = retry_after if retry_after else 60  # Default to 60 seconds
    time.sleep(wait_time)


def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """Calculate exponential backoff delay.

    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds

    Returns:
        Delay in seconds
    """
    delay = min(base_delay * (2**attempt), max_delay)
    return delay


def build_coin_network(coin: str, network: str | None = None) -> str:
    """Build coin-network identifier.

    Args:
        coin: Coin ticker (e.g., 'btc', 'eth')
        network: Network identifier (e.g., 'mainnet', 'bitcoin', 'ethereum')

    Returns:
        Coin-network identifier (e.g., 'btc-mainnet', 'eth-ethereum')
    """
    if network is None:
        return coin
    return f"{coin}-{network}"
