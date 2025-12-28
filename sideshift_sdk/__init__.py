"""SideShift.ai Python SDK - REST API V2 client library."""

from sideshift_sdk.client import AsyncSideShiftClient, SideShiftClient
from sideshift_sdk.exceptions import (
    SideShiftAPIError,
    SideShiftAuthenticationError,
    SideShiftException,
    SideShiftForbiddenError,
    SideShiftNotFoundError,
    SideShiftRateLimitError,
)

__version__ = "0.1.0"

__all__ = [
    "SideShiftClient",
    "AsyncSideShiftClient",
    "SideShiftException",
    "SideShiftAPIError",
    "SideShiftAuthenticationError",
    "SideShiftForbiddenError",
    "SideShiftNotFoundError",
    "SideShiftRateLimitError",
]

