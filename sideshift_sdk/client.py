"""Client classes for SideShift SDK."""

import asyncio
import inspect
import json
import logging
import os
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

import httpx
import requests

from sideshift_sdk.constants import (
    BASE_URL,
    CONTENT_TYPE_JSON,
    HEADER_ACCEPT,
    HEADER_CONTENT_TYPE,
    HEADER_REQUEST_ID,
    HEADER_SIDESHIFT_SECRET,
    HEADER_USER_AGENT,
    HEADER_USER_IP,
)
from sideshift_sdk.types import HeadersDict, JsonDict
from sideshift_sdk.exceptions import (
    SideShiftAPIError,
    SideShiftAuthenticationError,
    SideShiftException,
    SideShiftForbiddenError,
    SideShiftNetworkError,
    SideShiftNotFoundError,
    SideShiftRateLimitError,
    SideShiftSizeLimitError,
)
from sideshift_sdk.config import SDKConfig
from sideshift_sdk.logging_config import get_logger
from sideshift_sdk.utils import exponential_backoff

# Type aliases for hooks
RequestHook = Callable[[str, str, dict | None, dict | None, dict | None], None]
ResponseHook = Callable[[str, str, dict], None]
ErrorHook = Callable[[Exception, str, str], None]
AsyncRequestHook = Callable[[str, str, dict | None, dict | None, dict | None], Awaitable[None]]
AsyncResponseHook = Callable[[str, str, dict], Awaitable[None]]
AsyncErrorHook = Callable[[Exception, str, str], Awaitable[None]]


class BaseClient:
    """Base client with common functionality."""

    BASE_URL: str = BASE_URL  # Use constant from constants module

    def __init__(
        self,
        secret: str | None = None,
        affiliate_id: str | None = None,
        user_ip: str | None = None,
        base_url: str | None = None,
        api_version: str | None = None,
        enable_logging: bool = False,
        log_level: int | str | None = None,
    ):
        """Initialize client.

        Args:
            secret: SideShift account secret (x-sideshift-secret)
                   Can also be set via SIDESHIFT_SECRET environment variable
            affiliate_id: Affiliate ID (used in requests)
                          Can also be set via AFFILIATE_ID environment variable
            user_ip: End-user IP address (x-user-ip header)
                     Can also be set via SIDESHIFT_USER_IP environment variable
            base_url: Base URL for API (defaults to production)
                     If provided, takes precedence over api_version
            api_version: API version to use (e.g., "v2")
                        Can also be set via SIDESHIFT_API_VERSION environment variable
                        Default: "v2"
                        Only used if base_url is not provided
            enable_logging: Whether to enable logging (default: False)
            log_level: Logging level if enable_logging is True (default: logging.INFO)

        Raises:
            ValueError: If api_version is not supported
        """
        self.secret: str | None = secret or os.getenv("SIDESHIFT_SECRET")
        self.affiliate_id: str | None = affiliate_id or os.getenv("AFFILIATE_ID")
        self.user_ip: str | None = user_ip or os.getenv("SIDESHIFT_USER_IP")
        self.api_version: str = SDKConfig.get_api_version(api_version)
        self.base_url: str = SDKConfig.get_base_url(base_url, api_version=self.api_version)
        self._logger: logging.Logger = get_logger()
        self._enable_logging: bool = enable_logging
        
        if enable_logging and log_level is not None:
            import logging
            from sideshift_sdk.logging_config import configure_logging
            configure_logging(level=log_level)
        
        # Middleware hooks
        self._request_hooks: list[RequestHook | AsyncRequestHook] = []
        self._response_hooks: list[ResponseHook | AsyncResponseHook] = []
        self._error_hooks: list[ErrorHook | AsyncErrorHook] = []

    def set_secret(self, secret: str | None) -> None:
        """Update the secret key for authentication.

        This method allows rotating the secret without creating a new client instance.

        Args:
            secret: New secret key. If None, will attempt to read from SIDESHIFT_SECRET env var.
        """
        if secret is None:
            secret = os.getenv("SIDESHIFT_SECRET")
        self.secret = secret

    def __repr__(self) -> str:
        """String representation that doesn't expose secrets."""
        secret_display = "***" if self.secret else None
        return (
            f"{self.__class__.__name__}("
            f"secret={secret_display}, "
            f"affiliate_id={self.affiliate_id}, "
            f"base_url={self.base_url})"
        )

    def _get_headers(
        self, include_secret: bool = False, include_user_ip: bool = False, request_id: str | None = None
    ) -> HeadersDict:
        """Get request headers.

        Args:
            include_secret: Whether to include x-sideshift-secret header
            include_user_ip: Whether to include x-user-ip header
            request_id: Optional request ID to include in X-Request-ID header

        Returns:
            Headers dictionary
        """
        # Import here to avoid circular dependency
        from sideshift_sdk import __version__
        
        headers = {
            HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON,
            HEADER_ACCEPT: CONTENT_TYPE_JSON,
            HEADER_USER_AGENT: f"sideshift-sdk-python/{__version__}",
        }

        if include_secret and self.secret:
            headers[HEADER_SIDESHIFT_SECRET] = self.secret

        if include_user_ip and self.user_ip:
            headers[HEADER_USER_IP] = self.user_ip
        
        # Add X-Request-ID for correlation tracking
        if request_id:
            headers[HEADER_REQUEST_ID] = request_id
        elif HEADER_REQUEST_ID not in headers:
            headers[HEADER_REQUEST_ID] = str(uuid.uuid4())

        return headers

    def _merge_headers(
        self, sdk_headers: HeadersDict, user_headers: HeadersDict | None
    ) -> HeadersDict:
        """Merge user-provided headers with SDK-managed headers.

        This method protects SDK-managed headers from being overridden by user headers.
        SDK headers take precedence for: Content-Type, Accept, User-Agent, X-Request-ID.

        Args:
            sdk_headers: Headers managed by the SDK
            user_headers: Optional user-provided headers

        Returns:
            Merged headers dictionary with SDK headers taking precedence
        """
        if not user_headers:
            return sdk_headers.copy()

        # Headers that should be protected from user override
        protected_headers = {
            HEADER_CONTENT_TYPE.lower(),
            HEADER_ACCEPT.lower(),
            HEADER_USER_AGENT.lower(),
            HEADER_REQUEST_ID.lower(),
        }

        # Start with SDK headers (these take precedence)
        merged = sdk_headers.copy()

        # Add user headers, but skip protected ones
        for key, value in user_headers.items():
            key_lower = key.lower()
            if key_lower in protected_headers:
                # Check if user is trying to override a protected header
                if key_lower in {h.lower() for h in merged.keys()}:
                    if self._enable_logging:
                        self._logger.warning(
                            f"User-provided header '{key}' is protected and will be ignored. "
                            f"SDK-managed value will be used instead."
                        )
                # Don't add protected headers from user
                continue
            merged[key] = value

        return merged

    def add_request_hook(self, hook: RequestHook | AsyncRequestHook) -> None:
        """Add a request hook that will be called before each request.

        Args:
            hook: Callable that receives (method, endpoint, params, json_data, headers)
                  For async clients, hook can be async and will be awaited
        """
        self._request_hooks.append(hook)

    def add_response_hook(self, hook: ResponseHook | AsyncResponseHook) -> None:
        """Add a response hook that will be called after each successful request.

        Args:
            hook: Callable that receives (method, endpoint, response_data)
                  For async clients, hook can be async and will be awaited
        """
        self._response_hooks.append(hook)

    def add_error_hook(self, hook: ErrorHook | AsyncErrorHook) -> None:
        """Add an error hook that will be called when an exception occurs.

        Args:
            hook: Callable that receives (exception, method, endpoint)
                  For async clients, hook can be async and will be awaited
        """
        self._error_hooks.append(hook)

    def remove_request_hook(self, hook: RequestHook | AsyncRequestHook) -> None:
        """Remove a request hook.

        Args:
            hook: The hook to remove
        """
        if hook in self._request_hooks:
            self._request_hooks.remove(hook)

    def remove_response_hook(self, hook: ResponseHook | AsyncResponseHook) -> None:
        """Remove a response hook.

        Args:
            hook: The hook to remove
        """
        if hook in self._response_hooks:
            self._response_hooks.remove(hook)

    def remove_error_hook(self, hook: ErrorHook | AsyncErrorHook) -> None:
        """Remove an error hook.

        Args:
            hook: The hook to remove
        """
        if hook in self._error_hooks:
            self._error_hooks.remove(hook)

    def _handle_response(
        self,
        response: requests.Response | httpx.Response,
        request_id: str | None = None,
        method: str | None = None,
        endpoint: str | None = None,
        max_response_size: int | None = None,
    ) -> JsonDict:
        """Handle HTTP response and raise appropriate exceptions.

        Args:
            response: HTTP response object
            request_id: Request ID for correlation tracking (optional)
            method: HTTP method (GET, POST, etc.) for error context
            endpoint: API endpoint for error context
            max_response_size: Maximum response size in bytes (optional)

        Returns:
            Response JSON data

        Raises:
            SideShiftException: For various API errors
        """
        status_code = response.status_code
        
        # Include request_id in error response_data if available
        def add_request_id_to_error_data(error_data: dict | None) -> dict:
            """Add request_id to error_data if available.

            This helper function ensures that request_id is included in error response
            data for correlation tracking, creating a new dict if error_data is None.

            Args:
                error_data: Existing error data dict or None

            Returns:
                Error data dict with request_id added if available
            """
            if error_data is None:
                error_data = {}
            if request_id:
                error_data["request_id"] = request_id
            return error_data

        if status_code == 204:  # No Content
            return {}

        if status_code == 200 or status_code == 201:
            # Check response size if limit is configured
            if max_response_size is not None:
                content_length = None
                # Try to get Content-Length from headers
                if hasattr(response, "headers"):
                    content_length_str = response.headers.get("Content-Length") or response.headers.get("content-length")
                    if content_length_str:
                        try:
                            content_length = int(content_length_str)
                        except (ValueError, TypeError):
                            pass
                
                # If Content-Length is available and exceeds limit, raise error
                if content_length is not None and content_length > max_response_size:
                    error_msg = (
                        f"Response size ({content_length} bytes) exceeds maximum allowed size "
                        f"({max_response_size} bytes)"
                    )
                    if hasattr(self, "_enable_logging") and self._enable_logging:
                        self._logger.error(f"{error_msg} [Request-ID: {request_id}]")
                    raise SideShiftSizeLimitError(
                        error_msg,
                        response_data={"request_id": request_id, "size": content_length, "max_size": max_response_size} if request_id else {"size": content_length, "max_size": max_response_size},
                        request_id=request_id,
                        method=method,
                        endpoint=endpoint,
                    )
                
                # For responses without Content-Length, check actual content size
                # Only check if content is available and is bytes-like
                if content_length is None and hasattr(response, "content"):
                    try:
                        content = response.content
                        # Check if content is bytes-like (bytes, bytearray, etc.)
                        if isinstance(content, (bytes, bytearray)):
                            content_size = len(content)
                            if content_size > max_response_size:
                                error_msg = (
                                    f"Response size ({content_size} bytes) exceeds maximum allowed size "
                                    f"({max_response_size} bytes)"
                                )
                                if hasattr(self, "_enable_logging") and self._enable_logging:
                                    self._logger.error(f"{error_msg} [Request-ID: {request_id}]")
                                raise SideShiftSizeLimitError(
                                    error_msg,
                                    response_data={"request_id": request_id, "size": content_size, "max_size": max_response_size} if request_id else {"size": content_size, "max_size": max_response_size},
                                    request_id=request_id,
                                    method=method,
                                    endpoint=endpoint,
                                )
                    except (TypeError, AttributeError):
                        # If content is not available or not bytes-like, skip size check
                        # This can happen with streaming responses or Mock objects in tests
                        pass
            
            try:
                return response.json()
            except (ValueError, TypeError) as e:
                # JSON parsing failed - this should not happen for valid API responses
                # Try to get response text for error message
                error_text = "Unknown error"
                if hasattr(response, "text"):
                    error_text = response.text[:200] if response.text else "Empty response"
                elif hasattr(response, "content"):
                    try:
                        error_text = response.content.decode("utf-8")[:200]
                    except UnicodeDecodeError:
                        pass
                raise SideShiftAPIError(
                    f"Failed to parse JSON response: {str(e)}. Response: {error_text}",
                    status_code,
                    add_request_id_to_error_data({"raw_response": error_text}),
                    request_id=request_id,
                    method=method,
                    endpoint=endpoint,
                )

        # Handle rate limiting
        if status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
            if hasattr(self, "_enable_logging") and self._enable_logging:
                self._logger.warning(
                    f"Rate limit exceeded (429). Retry after: {retry_seconds}s" if retry_seconds else "Rate limit exceeded (429)"
                )
            error_data = {"retry_after": retry_seconds} if retry_seconds else {}
            raise SideShiftRateLimitError(
                "Rate limit exceeded",
                response_data=add_request_id_to_error_data(error_data) if error_data else add_request_id_to_error_data(None),
                request_id=request_id,
                method=method,
                endpoint=endpoint,
            )

        # Handle other errors
        try:
            error_data = response.json()
        except (ValueError, TypeError):
            # Handle both requests and httpx response types
            if hasattr(response, "text"):
                error_text = response.text
            elif hasattr(response, "content"):
                try:
                    error_text = response.content.decode("utf-8")
                except UnicodeDecodeError:
                    error_text = "Unknown error"
            else:
                error_text = "Unknown error"
            error_data = {"message": error_text or "Unknown error"}

        if status_code == 401:
            raise SideShiftAuthenticationError(
                error_data.get("message", "Authentication failed"),
                add_request_id_to_error_data(error_data),
                request_id=request_id,
                method=method,
                endpoint=endpoint,
            )
        elif status_code == 403:
            raise SideShiftForbiddenError(
                error_data.get("message", "Access forbidden"),
                add_request_id_to_error_data(error_data),
                request_id=request_id,
                method=method,
                endpoint=endpoint,
            )
        elif status_code == 404:
            raise SideShiftNotFoundError(
                error_data.get("message", "Resource not found"),
                add_request_id_to_error_data(error_data),
                request_id=request_id,
                method=method,
                endpoint=endpoint,
            )
        else:
            raise SideShiftAPIError(
                error_data.get("message", f"API error: {status_code}"),
                status_code,
                add_request_id_to_error_data(error_data),
                request_id=request_id,
                method=method,
                endpoint=endpoint,
            )


class SideShiftClient(BaseClient):
    """Synchronous client for SideShift API."""

    def __init__(
        self,
        secret: str | None = None,
        affiliate_id: str | None = None,
        user_ip: str | None = None,
        base_url: str | None = None,
        api_version: str | None = None,
        timeout: int | None = None,
        max_connections: int | None = None,
        max_keepalive_connections: int | None = None,
        verify_ssl: bool | None = None,
        proxy: str | dict[str, str] | None = None,
        max_retries: int | None = None,
        max_request_size: int | None = None,
        max_response_size: int | None = None,
        enable_logging: bool = False,
        log_level: int | str | None = None,
    ):
        """Initialize synchronous client.

        Args:
            secret: SideShift account secret
            affiliate_id: Affiliate ID
            user_ip: End-user IP address
            base_url: Base URL for API (can also be set via SIDESHIFT_BASE_URL env var)
                     If provided, takes precedence over api_version
            api_version: API version to use (e.g., "v2")
                        Can also be set via SIDESHIFT_API_VERSION env var
                        Default: "v2"
                        Only used if base_url is not provided
            timeout: Request timeout in seconds (can also be set via SIDESHIFT_TIMEOUT env var)
            max_connections: Maximum number of connections in pool (can also be set via SIDESHIFT_MAX_CONNECTIONS env var)
            max_keepalive_connections: Maximum number of keepalive connections (can also be set via SIDESHIFT_MAX_KEEPALIVE_CONNECTIONS env var)
            verify_ssl: Whether to verify SSL certificates (can also be set via SIDESHIFT_VERIFY_SSL env var, default: True)
            proxy: Proxy URL (string) or dict mapping protocol to URL (can also be set via SIDESHIFT_PROXY, HTTP_PROXY, or HTTPS_PROXY env vars)
            max_retries: Maximum number of retries for rate limits (can also be set via SIDESHIFT_MAX_RETRIES env var, default: 3)
            max_request_size: Maximum request body size in bytes (can also be set via SIDESHIFT_MAX_REQUEST_SIZE env var, default: 10MB)
            max_response_size: Maximum response body size in bytes (can also be set via SIDESHIFT_MAX_RESPONSE_SIZE env var, default: 50MB)
            enable_logging: Whether to enable logging (default: False)
            log_level: Logging level if enable_logging is True (default: logging.INFO)
        """
        super().__init__(secret, affiliate_id, user_ip, base_url, api_version, enable_logging, log_level)
        self.timeout: int = SDKConfig.get_timeout(timeout)
        self.max_connections: int = SDKConfig.get_max_connections(max_connections)
        self.max_keepalive_connections: int = SDKConfig.get_max_keepalive_connections(max_keepalive_connections)
        self.max_request_size: int = SDKConfig.get_max_request_size(max_request_size)
        self.max_response_size: int = SDKConfig.get_max_response_size(max_response_size)
        self.verify_ssl: bool = SDKConfig.get_verify_ssl(verify_ssl)
        self.proxy: str | dict[str, str] | None = SDKConfig.get_proxy(proxy)
        self.max_retries: int = SDKConfig.get_max_retries(max_retries)
        
        # Configure connection pooling
        self._session: requests.Session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=self.max_connections,
            pool_maxsize=self.max_connections,
            max_retries=0,  # We handle retries ourselves
            pool_block=False,
        )
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def _request(
        self,
        method: str,
        endpoint: str,
        params: JsonDict | None = None,
        json_data: JsonDict | None = None,
        headers: HeadersDict | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
        max_retries: int | None = None,
        timeout: int | None = None,
    ) -> JsonDict:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json_data: JSON body data
            headers: Additional headers
            require_auth: Whether authentication is required
            require_user_ip: Whether user IP header is required
            max_retries: Maximum number of retries for rate limits (if None, uses client-level max_retries)
            timeout: Request timeout in seconds (if None, uses client-level timeout)

        Returns:
            Response JSON data
        """
        # Use client-level max_retries if not provided, otherwise use provided value
        retry_count = self.max_retries if max_retries is None else max_retries
        # Use client-level timeout if not provided, otherwise use provided value
        request_timeout = self.timeout if timeout is None else timeout
        url = f"{self.base_url}{endpoint}"
        
        # Generate request ID if not provided by user
        request_id = None
        if headers and HEADER_REQUEST_ID in headers:
            request_id = headers[HEADER_REQUEST_ID]
        else:
            request_id = str(uuid.uuid4())
        
        # Get SDK headers with request ID
        sdk_headers = self._get_headers(
            include_secret=require_auth, include_user_ip=require_user_ip, request_id=request_id
        )
        
        # Merge user headers (protected headers will be ignored)
        request_headers = self._merge_headers(sdk_headers, headers)

        # Validate request body size if json_data is provided
        if json_data is not None and self.max_request_size is not None:
            try:
                request_body = json.dumps(json_data)
                request_size = len(request_body.encode("utf-8"))
                if request_size > self.max_request_size:
                    error_msg = (
                        f"Request body size ({request_size} bytes) exceeds maximum allowed size "
                        f"({self.max_request_size} bytes)"
                    )
                    if self._enable_logging:
                        self._logger.error(f"{error_msg} [Request-ID: {request_id}]")
                    raise SideShiftSizeLimitError(
                        error_msg,
                        response_data={"request_id": request_id, "size": request_size, "max_size": self.max_request_size} if request_id else {"size": request_size, "max_size": self.max_request_size},
                        request_id=request_id,
                        method=method,
                        endpoint=endpoint,
                    )
            except (TypeError, ValueError) as e:
                # If JSON serialization fails, let the request library handle it
                if self._enable_logging:
                    self._logger.warning(f"Could not validate request size: {e}")

        for attempt in range(retry_count + 1):
            try:
                if self._enable_logging:
                    self._logger.debug(
                        f"Request: {method} {endpoint} (attempt {attempt + 1}/{retry_count + 1}) [Request-ID: {request_id}]"
                    )
                    if params:
                        self._logger.debug(f"  Params: {params}")
                
                # Call request hooks
                for hook in self._request_hooks:
                    try:
                        hook(method, endpoint, params, json_data, request_headers)
                    except Exception as hook_error:
                        # Don't let hook errors break the request
                        if self._enable_logging:
                            self._logger.warning(f"Request hook error: {hook_error}")
                
                response = self._session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=request_headers,
                    timeout=request_timeout,
                    verify=self.verify_ssl,
                    proxies=self.proxy if self.proxy else None,
                )

                # Extract request ID from response headers if present (API may echo it back)
                response_request_id = response.headers.get(HEADER_REQUEST_ID.lower()) or response.headers.get(HEADER_REQUEST_ID)
                
                if self._enable_logging:
                    log_msg = f"Response: {method} {endpoint} - {response.status_code} [Request-ID: {request_id}]"
                    if response_request_id and response_request_id != request_id:
                        log_msg += f" [Response-Request-ID: {response_request_id}]"
                    self._logger.debug(log_msg)

                response_data = self._handle_response(
                    response, 
                    request_id=request_id, 
                    method=method, 
                    endpoint=endpoint,
                    max_response_size=self.max_response_size,
                )
                
                # Call response hooks
                for hook in self._response_hooks:
                    try:
                        hook(method, endpoint, response_data)
                    except Exception as hook_error:
                        # Don't let hook errors break the response
                        if self._enable_logging:
                            self._logger.warning(f"Response hook error: {hook_error}")
                
                return response_data

            except SideShiftRateLimitError:
                if self._enable_logging:
                    self._logger.warning(
                        f"Rate limit exceeded for {method} {endpoint} (attempt {attempt + 1}/{retry_count + 1}) [Request-ID: {request_id}]"
                    )
                if attempt < retry_count:
                    wait_time = exponential_backoff(attempt)
                    if self._enable_logging:
                        self._logger.debug(f"Retrying after {wait_time:.2f}s")
                    time.sleep(wait_time)
                    continue
                raise
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                # Network errors - raise SDK exception with better message
                error_msg = f"Network error: {str(e)}"
                if isinstance(e, requests.exceptions.Timeout):
                    error_msg = f"Request timeout after {self.timeout} seconds"
                if self._enable_logging:
                    self._logger.error(f"Network error for {method} {endpoint} [Request-ID: {request_id}]: {error_msg}")
                network_error = SideShiftNetworkError(
                    error_msg,
                    response_data={"request_id": request_id} if request_id else None,
                    request_id=request_id,
                    method=method,
                    endpoint=endpoint,
                )
                # Call error hooks
                for hook in self._error_hooks:
                    try:
                        hook(network_error, method, endpoint)
                    except Exception as hook_error:
                        if self._enable_logging:
                            self._logger.warning(f"Error hook error: {hook_error}")
                raise network_error from e
            except requests.exceptions.RequestException as e:
                # Other requests exceptions (DNS, SSL, etc.)
                if self._enable_logging:
                    self._logger.error(f"Request exception for {method} {endpoint} [Request-ID: {request_id}]: {str(e)}")
                network_error = SideShiftNetworkError(
                    f"Network request failed: {str(e)}",
                    response_data={"request_id": request_id} if request_id else None,
                    request_id=request_id,
                    method=method,
                    endpoint=endpoint,
                )
                # Call error hooks
                for hook in self._error_hooks:
                    try:
                        hook(network_error, method, endpoint)
                    except Exception as hook_error:
                        if self._enable_logging:
                            self._logger.warning(f"Error hook error: {hook_error}")
                raise network_error from e
            except SideShiftException as e:
                # Call error hooks for SDK exceptions
                for hook in self._error_hooks:
                    try:
                        hook(e, method, endpoint)
                    except Exception as hook_error:
                        if self._enable_logging:
                            self._logger.warning(f"Error hook error: {hook_error}")
                raise

    def get(
        self,
        endpoint: str,
        params: JsonDict | None = None,
        headers: HeadersDict | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
        timeout: int | None = None,
    ) -> JsonDict:
        """Make GET request.

        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            require_auth: Whether authentication is required
            require_user_ip: Whether user IP header is required
            timeout: Request timeout in seconds (if None, uses client-level timeout)

        Returns:
            Response JSON data
        """
        return self._request(
            "GET",
            endpoint,
            params=params,
            headers=headers,
            require_auth=require_auth,
            require_user_ip=require_user_ip,
            timeout=timeout,
        )

    def post(
        self,
        endpoint: str,
        json_data: JsonDict | None = None,
        headers: HeadersDict | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
        timeout: int | None = None,
    ) -> JsonDict:
        """Make POST request.

        Args:
            endpoint: API endpoint
            json_data: JSON body data
            headers: Additional headers
            require_auth: Whether authentication is required
            require_user_ip: Whether user IP header is required
            timeout: Request timeout in seconds (if None, uses client-level timeout)

        Returns:
            Response JSON data
        """
        return self._request(
            "POST",
            endpoint,
            json_data=json_data,
            headers=headers,
            require_auth=require_auth,
            require_user_ip=require_user_ip,
            timeout=timeout,
        )

    def get_binary(
        self,
        endpoint: str,
        headers: HeadersDict | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
        timeout: int | None = None,
    ) -> bytes:
        """Make GET request and return binary response.

        Args:
            endpoint: API endpoint
            headers: Additional headers
            require_auth: Whether authentication is required
            require_user_ip: Whether user IP header is required
            timeout: Request timeout in seconds (if None, uses client-level timeout)

        Returns:
            Response binary data
        """
        url = f"{self.base_url}{endpoint}"
        sdk_headers = self._get_headers(
            include_secret=require_auth, include_user_ip=require_user_ip
        )
        request_headers = self._merge_headers(sdk_headers, headers)
        # Use client-level timeout if not provided, otherwise use provided value
        request_timeout = self.timeout if timeout is None else timeout

        response = self._session.get(
            url,
            headers=request_headers,
            timeout=request_timeout,
        )

        if response.status_code != 200:
            self._handle_response(
                response, 
                method="GET", 
                endpoint=endpoint,
                max_response_size=self.max_response_size,
            )
            return b""

        return response.content

    def close(self) -> None:
        """Close the HTTP session and release resources.

        This method closes the underlying `requests.Session` object, which releases
        all connection pools and network resources. After calling this method,
        the client should not be used for making requests.

        Note:
            It's safe to call this method multiple times. If the session is already
            closed, subsequent calls will have no effect.

        Example:
            >>> client = SideShiftClient(secret="...")
            >>> # ... use client ...
            >>> client.close()  # Clean up resources
        """
        self._session.close()

    def __enter__(self) -> "SideShiftClient":
        """Context manager entry.

        Allows the client to be used as a context manager with the `with` statement.
        Automatically closes the session when exiting the context.

        Returns:
            The client instance itself

        Example:
            >>> with SideShiftClient(secret="...") as client:
            ...     coins = client.get("/coins")
        """
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit.

        Automatically closes the HTTP session when exiting the context.
        This ensures proper cleanup of network resources.

        If an error occurs during cleanup, it is logged but does not suppress
        exceptions that occurred in the context body. If both a context body
        exception and a cleanup exception occur, the context body exception
        takes precedence.

        Args:
            exc_type: Exception type if an exception occurred in the context body
            exc_val: Exception value if an exception occurred in the context body
            exc_tb: Exception traceback if an exception occurred in the context body

        Returns:
            None (exceptions are not suppressed)
        """
        try:
            self.close()
        except Exception as cleanup_error:
            # Log the cleanup error but don't suppress the original exception
            if self._enable_logging:
                self._logger.error(
                    f"Error during context manager cleanup: {cleanup_error}",
                    exc_info=True,
                )
            # If there was an exception in the context body, preserve it
            # If there wasn't, raise the cleanup error
            if exc_type is None:
                raise
            # If both exist, log the cleanup error but let the original propagate
            # This follows Python's context manager protocol best practices


class AsyncSideShiftClient(BaseClient):
    """Asynchronous client for SideShift API."""

    def __init__(
        self,
        secret: str | None = None,
        affiliate_id: str | None = None,
        user_ip: str | None = None,
        base_url: str | None = None,
        api_version: str | None = None,
        timeout: int | None = None,
        max_connections: int | None = None,
        max_keepalive_connections: int | None = None,
        verify_ssl: bool | None = None,
        proxy: str | dict[str, str] | None = None,
        max_retries: int | None = None,
        max_request_size: int | None = None,
        max_response_size: int | None = None,
        enable_logging: bool = False,
        log_level: int | str | None = None,
    ):
        """Initialize asynchronous client.

        Args:
            secret: SideShift account secret
            affiliate_id: Affiliate ID
            user_ip: End-user IP address
            base_url: Base URL for API (can also be set via SIDESHIFT_BASE_URL env var)
                     If provided, takes precedence over api_version
            api_version: API version to use (e.g., "v2")
                        Can also be set via SIDESHIFT_API_VERSION env var
                        Default: "v2"
                        Only used if base_url is not provided
            timeout: Request timeout in seconds (can also be set via SIDESHIFT_TIMEOUT env var)
            max_connections: Maximum number of connections in pool (can also be set via SIDESHIFT_MAX_CONNECTIONS env var)
            max_keepalive_connections: Maximum number of keepalive connections (can also be set via SIDESHIFT_MAX_KEEPALIVE_CONNECTIONS env var)
            verify_ssl: Whether to verify SSL certificates (can also be set via SIDESHIFT_VERIFY_SSL env var, default: True)
            proxy: Proxy URL (string) or dict mapping protocol to URL (can also be set via SIDESHIFT_PROXY, HTTP_PROXY, or HTTPS_PROXY env vars)
            max_retries: Maximum number of retries for rate limits (can also be set via SIDESHIFT_MAX_RETRIES env var, default: 3)
            max_request_size: Maximum request body size in bytes (can also be set via SIDESHIFT_MAX_REQUEST_SIZE env var, default: 10MB)
            max_response_size: Maximum response body size in bytes (can also be set via SIDESHIFT_MAX_RESPONSE_SIZE env var, default: 50MB)
            enable_logging: Whether to enable logging (default: False)
            log_level: Logging level if enable_logging is True (default: logging.INFO)
        """
        super().__init__(secret, affiliate_id, user_ip, base_url, api_version, enable_logging, log_level)
        self.timeout: int = SDKConfig.get_timeout(timeout)
        self.max_connections: int = SDKConfig.get_max_connections(max_connections)
        self.max_keepalive_connections: int = SDKConfig.get_max_keepalive_connections(max_keepalive_connections)
        self.verify_ssl: bool = SDKConfig.get_verify_ssl(verify_ssl)
        self.proxy: str | dict[str, str] | None = SDKConfig.get_proxy(proxy)
        self.max_retries: int = SDKConfig.get_max_retries(max_retries)
        self.max_request_size: int = SDKConfig.get_max_request_size(max_request_size)
        self.max_response_size: int = SDKConfig.get_max_response_size(max_response_size)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client.

        This method implements lazy initialization of the `httpx.AsyncClient`.
        The client is created on first use and reused for subsequent requests,
        enabling connection pooling and efficient resource usage.

        Returns:
            The async HTTP client instance, creating it if it doesn't exist

        Note:
            The client is configured with connection pooling limits, SSL verification,
            and timeout settings based on the client's configuration.
        """
        if self._client is None:
            limits = httpx.Limits(
                max_connections=self.max_connections,
                max_keepalive_connections=self.max_keepalive_connections,
            )
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=limits,
                verify=self.verify_ssl,
            )
        return self._client

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: JsonDict | None = None,
        json_data: JsonDict | None = None,
        headers: HeadersDict | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
        max_retries: int | None = None,
        timeout: int | None = None,
    ) -> JsonDict:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json_data: JSON body data
            headers: Additional headers
            require_auth: Whether authentication is required
            require_user_ip: Whether user IP header is required
            max_retries: Maximum number of retries for rate limits (if None, uses client-level max_retries)
            timeout: Request timeout in seconds (if None, uses client-level timeout)

        Returns:
            Response JSON data
        """
        # Use client-level max_retries if not provided, otherwise use provided value
        retry_count = self.max_retries if max_retries is None else max_retries
        # Use client-level timeout if not provided, otherwise use provided value
        request_timeout = self.timeout if timeout is None else timeout
        url = f"{self.base_url}{endpoint}"
        
        # Generate request ID if not provided by user
        request_id = None
        if headers and HEADER_REQUEST_ID in headers:
            request_id = headers[HEADER_REQUEST_ID]
        else:
            request_id = str(uuid.uuid4())
        
        # Get SDK headers with request ID
        sdk_headers = self._get_headers(
            include_secret=require_auth, include_user_ip=require_user_ip, request_id=request_id
        )
        
        # Merge user headers (protected headers will be ignored)
        request_headers = self._merge_headers(sdk_headers, headers)

        # Validate request body size if json_data is provided
        if json_data is not None and self.max_request_size is not None:
            try:
                request_body = json.dumps(json_data)
                request_size = len(request_body.encode("utf-8"))
                if request_size > self.max_request_size:
                    error_msg = (
                        f"Request body size ({request_size} bytes) exceeds maximum allowed size "
                        f"({self.max_request_size} bytes)"
                    )
                    if self._enable_logging:
                        self._logger.error(f"{error_msg} [Request-ID: {request_id}]")
                    raise SideShiftSizeLimitError(
                        error_msg,
                        response_data={"request_id": request_id, "size": request_size, "max_size": self.max_request_size} if request_id else {"size": request_size, "max_size": self.max_request_size},
                        request_id=request_id,
                        method=method,
                        endpoint=endpoint,
                    )
            except (TypeError, ValueError) as e:
                # If JSON serialization fails, let the request library handle it
                if self._enable_logging:
                    self._logger.warning(f"Could not validate request size: {e}")

        client = await self._get_client()

        for attempt in range(retry_count + 1):
            try:
                if self._enable_logging:
                    self._logger.debug(
                        f"Request: {method} {endpoint} (attempt {attempt + 1}/{retry_count + 1}) [Request-ID: {request_id}]"
                    )
                    if params:
                        self._logger.debug(f"  Params: {params}")
                
                # Call request hooks (support both sync and async)
                for hook in self._request_hooks:
                    try:
                        if inspect.iscoroutinefunction(hook):
                            await hook(method, endpoint, params, json_data, request_headers)
                        else:
                            hook(method, endpoint, params, json_data, request_headers)
                    except Exception as hook_error:
                        # Don't let hook errors break the request
                        if self._enable_logging:
                            self._logger.warning(f"Request hook error: {hook_error}")
                
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=request_headers,
                    timeout=request_timeout,
                )

                # Extract request ID from response headers if present (API may echo it back)
                response_request_id = response.headers.get(HEADER_REQUEST_ID.lower()) or response.headers.get(HEADER_REQUEST_ID)
                
                if self._enable_logging:
                    log_msg = f"Response: {method} {endpoint} - {response.status_code} [Request-ID: {request_id}]"
                    if response_request_id and response_request_id != request_id:
                        log_msg += f" [Response-Request-ID: {response_request_id}]"
                    self._logger.debug(log_msg)

                response_data = self._handle_response(
                    response, 
                    request_id=request_id, 
                    method=method, 
                    endpoint=endpoint,
                    max_response_size=self.max_response_size,
                )
                
                # Call response hooks (support both sync and async)
                for hook in self._response_hooks:
                    try:
                        if inspect.iscoroutinefunction(hook):
                            await hook(method, endpoint, response_data)
                        else:
                            hook(method, endpoint, response_data)
                    except Exception as hook_error:
                        # Don't let hook errors break the response
                        if self._enable_logging:
                            self._logger.warning(f"Response hook error: {hook_error}")
                
                return response_data

            except SideShiftRateLimitError:
                if self._enable_logging:
                    self._logger.warning(
                        f"Rate limit exceeded for {method} {endpoint} (attempt {attempt + 1}/{retry_count + 1}) [Request-ID: {request_id}]"
                    )
                if attempt < retry_count:
                    wait_time = exponential_backoff(attempt)
                    if self._enable_logging:
                        self._logger.debug(f"Retrying after {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    continue
                raise
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                # Network errors - raise SDK exception with better message
                error_msg = f"Network error: {str(e)}"
                if isinstance(e, httpx.TimeoutException):
                    error_msg = f"Request timeout after {self.timeout} seconds"
                if self._enable_logging:
                    self._logger.error(f"Network error for {method} {endpoint} [Request-ID: {request_id}]: {error_msg}")
                raise SideShiftNetworkError(
                    error_msg,
                    response_data={"request_id": request_id} if request_id else None,
                    request_id=request_id,
                    method=method,
                    endpoint=endpoint,
                ) from e
            except asyncio.CancelledError:
                # Request was cancelled - re-raise to allow proper cancellation
                if self._enable_logging:
                    self._logger.debug(f"Request cancelled: {method} {endpoint} [Request-ID: {request_id}]")
                raise
            except httpx.RequestError as e:
                # Other httpx exceptions (DNS, SSL, etc.)
                if self._enable_logging:
                    self._logger.error(f"Request error for {method} {endpoint} [Request-ID: {request_id}]: {str(e)}")
                network_error = SideShiftNetworkError(
                    f"Network request failed: {str(e)}",
                    response_data={"request_id": request_id} if request_id else None,
                    request_id=request_id,
                    method=method,
                    endpoint=endpoint,
                )
                # Call error hooks (support both sync and async)
                for hook in self._error_hooks:
                    try:
                        if inspect.iscoroutinefunction(hook):
                            await hook(network_error, method, endpoint)
                        else:
                            hook(network_error, method, endpoint)
                    except Exception as hook_error:
                        if self._enable_logging:
                            self._logger.warning(f"Error hook error: {hook_error}")
                raise network_error from e
            except SideShiftException as e:
                # Call error hooks for SDK exceptions (support both sync and async)
                for hook in self._error_hooks:
                    try:
                        if inspect.iscoroutinefunction(hook):
                            await hook(e, method, endpoint)
                        else:
                            hook(e, method, endpoint)
                    except Exception as hook_error:
                        if self._enable_logging:
                            self._logger.warning(f"Error hook error: {hook_error}")
                raise

    async def get(
        self,
        endpoint: str,
        params: JsonDict | None = None,
        headers: HeadersDict | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
        timeout: int | None = None,
    ) -> JsonDict:
        """Make GET request.

        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            require_auth: Whether authentication is required
            require_user_ip: Whether user IP header is required
            timeout: Request timeout in seconds (if None, uses client-level timeout)

        Returns:
            Response JSON data
        """
        return await self._request(
            "GET",
            endpoint,
            params=params,
            headers=headers,
            require_auth=require_auth,
            require_user_ip=require_user_ip,
            timeout=timeout,
        )

    async def get_binary(
        self,
        endpoint: str,
        headers: HeadersDict | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
        timeout: int | None = None,
    ) -> bytes:
        """Make GET request and return binary response.

        Args:
            endpoint: API endpoint
            headers: Additional headers
            require_auth: Whether authentication is required
            require_user_ip: Whether user IP header is required
            timeout: Request timeout in seconds (if None, uses client-level timeout)

        Returns:
            Response binary data
        """
        url = f"{self.base_url}{endpoint}"
        sdk_headers = self._get_headers(
            include_secret=require_auth, include_user_ip=require_user_ip
        )
        request_headers = self._merge_headers(sdk_headers, headers)
        # Use client-level timeout if not provided, otherwise use provided value
        request_timeout = self.timeout if timeout is None else timeout

        client = await self._get_client()
        response = await client.get(
            url,
            headers=request_headers,
            timeout=request_timeout,
        )

        if response.status_code != 200:
            self._handle_response(
                response, 
                method="GET", 
                endpoint=endpoint,
                max_response_size=self.max_response_size,
            )
            return b""

        return response.content

    async def post(
        self,
        endpoint: str,
        json_data: JsonDict | None = None,
        headers: HeadersDict | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
        timeout: int | None = None,
    ) -> JsonDict:
        """Make POST request.

        Args:
            endpoint: API endpoint
            json_data: JSON body data
            headers: Additional headers
            require_auth: Whether authentication is required
            require_user_ip: Whether user IP header is required
            timeout: Request timeout in seconds (if None, uses client-level timeout)

        Returns:
            Response JSON data
        """
        return await self._request(
            "POST",
            endpoint,
            json_data=json_data,
            headers=headers,
            require_auth=require_auth,
            require_user_ip=require_user_ip,
            timeout=timeout,
        )

    async def close(self) -> None:
        """Close the async HTTP client and release resources.

        This method closes the underlying `httpx.AsyncClient` object, which releases
        all connection pools and network resources. After calling this method,
        the client should not be used for making requests.

        Note:
            It's safe to call this method multiple times. If the client is already
            closed, subsequent calls will have no effect.

        Example:
            >>> client = AsyncSideShiftClient(secret="...")
            >>> # ... use client ...
            >>> await client.close()  # Clean up resources
        """
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "AsyncSideShiftClient":
        """Async context manager entry.

        Allows the async client to be used as an async context manager with the `async with` statement.
        Automatically closes the async client session when exiting the context.

        Returns:
            The async client instance itself

        Example:
            >>> async with AsyncSideShiftClient(secret="...") as client:
            ...     coins = await client.get("/coins")
        """
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit.

        Automatically closes the async HTTP client when exiting the context.
        This ensures proper cleanup of network resources and connection pools.

        If an error occurs during cleanup, it is logged but does not suppress
        exceptions that occurred in the context body. If both a context body
        exception and a cleanup exception occur, the context body exception
        takes precedence.

        Args:
            exc_type: Exception type if an exception occurred in the context body
            exc_val: Exception value if an exception occurred in the context body
            exc_tb: Exception traceback if an exception occurred in the context body

        Returns:
            None (exceptions are not suppressed)
        """
        try:
            await self.close()
        except Exception as cleanup_error:
            # Log the cleanup error but don't suppress the original exception
            if self._enable_logging:
                self._logger.error(
                    f"Error during async context manager cleanup: {cleanup_error}",
                    exc_info=True,
                )
            # If there was an exception in the context body, preserve it
            # If there wasn't, raise the cleanup error
            if exc_type is None:
                raise
            # If both exist, log the cleanup error but let the original propagate
            # This follows Python's context manager protocol best practices
