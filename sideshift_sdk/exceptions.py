"""Custom exceptions for SideShift SDK."""


class SideShiftException(Exception):
    """Base exception for all SideShift SDK errors."""

    def __init__(
        self, message: str, status_code: int | None = None, response_data: dict | None = None
    ):
        """Initialize exception.

        Args:
            message: Error message
            status_code: HTTP status code if applicable
            response_data: Response data from API if applicable
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data


class SideShiftAPIError(SideShiftException):
    """Raised when API returns an error (400, 500)."""

    def __init__(self, message: str, status_code: int, response_data: dict | None = None):
        """Initialize API error.

        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Response data from API
        """
        super().__init__(message, status_code, response_data)
        self.status_code = status_code


class SideShiftAuthenticationError(SideShiftException):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str = "Authentication failed", response_data: dict | None = None):
        """Initialize authentication error.

        Args:
            message: Error message
            response_data: Response data from API
        """
        super().__init__(message, 401, response_data)


class SideShiftForbiddenError(SideShiftException):
    """Raised when access is forbidden (403)."""

    def __init__(self, message: str = "Access forbidden", response_data: dict | None = None):
        """Initialize forbidden error.

        Args:
            message: Error message
            response_data: Response data from API
        """
        super().__init__(message, 403, response_data)


class SideShiftNotFoundError(SideShiftException):
    """Raised when resource is not found (404)."""

    def __init__(self, message: str = "Resource not found", response_data: dict | None = None):
        """Initialize not found error.

        Args:
            message: Error message
            response_data: Response data from API
        """
        super().__init__(message, 404, response_data)


class SideShiftRateLimitError(SideShiftException):
    """Raised when rate limit is exceeded (429)."""

    def __init__(self, message: str = "Rate limit exceeded", response_data: dict | None = None):
        """Initialize rate limit error.

        Args:
            message: Error message
            response_data: Response data from API
        """
        super().__init__(message, 429, response_data)
