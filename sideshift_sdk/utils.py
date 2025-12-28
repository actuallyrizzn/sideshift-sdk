"""Utility functions for SideShift SDK."""

import time
from typing import Any


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
    if network:
        return f"{coin}-{network}"
    return coin

