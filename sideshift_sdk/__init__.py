"""SideShift.ai Python SDK - REST API V2 client library."""

import sys

# Check Python version compatibility
if sys.version_info < (3, 8):
    raise RuntimeError(
        "sideshift-sdk requires Python 3.8 or higher. "
        f"Current version: {sys.version_info.major}.{sys.version_info.minor}"
    )

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
