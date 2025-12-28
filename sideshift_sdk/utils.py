"""Utility functions for SideShift SDK."""

from typing import Any


def validate_non_empty_string(value: str | None, param_name: str) -> None:
    """Validate that a string parameter is not None and not empty.

    Args:
        value: The value to validate
        param_name: Name of the parameter for error messages

    Raises:
        ValueError: If value is None or empty string
        TypeError: If value or param_name is not the expected type
    """
    if not isinstance(param_name, str):
        raise TypeError(f"param_name must be a string, got {type(param_name).__name__}")
    if not param_name.strip():
        raise ValueError("param_name cannot be empty")
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
        TypeError: If amount or param_name is not the expected type
    """
    if not isinstance(param_name, str):
        raise TypeError(f"param_name must be a string, got {type(param_name).__name__}")
    if not param_name.strip():
        raise ValueError("param_name cannot be empty")
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


def validate_response_data(response_data: Any, expected_type: type = dict) -> dict | list[dict]:
    """Validate that response data matches expected type.

    Args:
        response_data: Response data from API
        expected_type: Expected type (dict or list)

    Returns:
        Validated response data

    Raises:
        TypeError: If response data doesn't match expected type or expected_type is invalid
        ValueError: If list contains non-dict items
    """
    if not isinstance(expected_type, type):
        raise TypeError(f"expected_type must be a type, got {type(expected_type).__name__}")
    if expected_type not in (dict, list):
        raise ValueError(f"expected_type must be dict or list, got {expected_type.__name__}")
    if expected_type == dict:
        if not isinstance(response_data, dict):
            raise TypeError(
                f"Expected dict response, got {type(response_data).__name__}: {response_data}"
            )
        return response_data
    elif expected_type == list:
        if not isinstance(response_data, list):
            raise TypeError(
                f"Expected list response, got {type(response_data).__name__}: {response_data}"
            )
        # Validate all items in list are dicts
        for i, item in enumerate(response_data):
            if not isinstance(item, dict):
                raise ValueError(
                    f"Expected list of dicts, but item at index {i} is {type(item).__name__}: {item}"
                )
        return response_data
    else:
        raise ValueError(f"Unsupported expected_type: {expected_type}")


def normalize_affiliate_id(affiliate_id: str | None) -> str | None:
    """Normalize affiliate_id: treat empty strings as None.

    Args:
        affiliate_id: Affiliate ID string (may be empty)

    Returns:
        None if affiliate_id is None or empty string, otherwise the string

    Raises:
        TypeError: If affiliate_id is not a string or None
    """
    if affiliate_id is not None and not isinstance(affiliate_id, str):
        raise TypeError(f"affiliate_id must be a string or None, got {type(affiliate_id).__name__}")
    if affiliate_id is None:
        return None
    if not affiliate_id.strip():
        return None
    return affiliate_id


def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """Calculate exponential backoff delay.

    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds

    Returns:
        Delay in seconds

    Raises:
        TypeError: If attempt is not an int or delays are not numbers
        ValueError: If attempt is negative or delays are non-positive
    """
    if not isinstance(attempt, int):
        raise TypeError(f"attempt must be an int, got {type(attempt).__name__}")
    if attempt < 0:
        raise ValueError(f"attempt must be non-negative, got {attempt}")
    if not isinstance(base_delay, (int, float)):
        raise TypeError(f"base_delay must be a number, got {type(base_delay).__name__}")
    if base_delay <= 0:
        raise ValueError(f"base_delay must be positive, got {base_delay}")
    if not isinstance(max_delay, (int, float)):
        raise TypeError(f"max_delay must be a number, got {type(max_delay).__name__}")
    if max_delay <= 0:
        raise ValueError(f"max_delay must be positive, got {max_delay}")
    if max_delay < base_delay:
        raise ValueError(f"max_delay ({max_delay}) must be >= base_delay ({base_delay})")
    delay = min(base_delay * (2**attempt), max_delay)
    return delay


