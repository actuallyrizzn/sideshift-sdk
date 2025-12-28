"""Type aliases for SideShift SDK."""

from typing import Any

# API response/request data types
JsonDict = dict[str, Any]
"""Type alias for JSON-compatible dictionary (API request/response data)."""

HeadersDict = dict[str, str]
"""Type alias for HTTP headers dictionary."""

ResponseData = dict[str, Any]
"""Type alias for API response data."""
