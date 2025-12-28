"""Client classes for SideShift SDK."""

import inspect
import os
import time
from collections.abc import Awaitable, Callable
from typing import Any

import httpx
import requests

from sideshift_sdk.constants import (
    BASE_URL,
    CONTENT_TYPE_JSON,
    HEADER_ACCEPT,
    HEADER_CONTENT_TYPE,
    HEADER_SIDESHIFT_SECRET,
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

    BASE_URL = BASE_URL  # Use constant from constants module

    def __init__(
        self,
        secret: str | None = None,
        affiliate_id: str | None = None,
        user_ip: str | None = None,
        base_url: str | None = None,
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
            enable_logging: Whether to enable logging (default: False)
            log_level: Logging level if enable_logging is True (default: logging.INFO)
        """
        self.secret = secret or os.getenv("SIDESHIFT_SECRET")
        self.affiliate_id = affiliate_id or os.getenv("AFFILIATE_ID")
        self.user_ip = user_ip or os.getenv("SIDESHIFT_USER_IP")
        self.base_url = SDKConfig.get_base_url(base_url)
        self._logger = get_logger()
        self._enable_logging = enable_logging
        
        if enable_logging and log_level is not None:
            import logging
            from sideshift_sdk.logging_config import configure_logging
            configure_logging(level=log_level)
        
        # Middleware hooks
        self._request_hooks: list[RequestHook | AsyncRequestHook] = []
        self._response_hooks: list[ResponseHook | AsyncResponseHook] = []
        self._error_hooks: list[ErrorHook | AsyncErrorHook] = []

    def _get_headers(
        self, include_secret: bool = False, include_user_ip: bool = False
    ) -> HeadersDict:
        """Get request headers.

        Args:
            include_secret: Whether to include x-sideshift-secret header
            include_user_ip: Whether to include x-user-ip header

        Returns:
            Headers dictionary
        """
        headers = {
            HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON,
            HEADER_ACCEPT: CONTENT_TYPE_JSON,
        }

        if include_secret and self.secret:
            headers[HEADER_SIDESHIFT_SECRET] = self.secret

        if include_user_ip and self.user_ip:
            headers[HEADER_USER_IP] = self.user_ip

        return headers

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

    def _handle_response(self, response: requests.Response | httpx.Response) -> JsonDict:
        """Handle HTTP response and raise appropriate exceptions.

        Args:
            response: HTTP response object

        Returns:
            Response JSON data

        Raises:
            SideShiftException: For various API errors
        """
        status_code = response.status_code

        if status_code == 204:  # No Content
            return {}

        if status_code == 200 or status_code == 201:
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
                    {"raw_response": error_text},
                )

        # Handle rate limiting
        if status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
            if hasattr(self, "_enable_logging") and self._enable_logging:
                self._logger.warning(
                    f"Rate limit exceeded (429). Retry after: {retry_seconds}s" if retry_seconds else "Rate limit exceeded (429)"
                )
            raise SideShiftRateLimitError(
                "Rate limit exceeded",
                response_data={"retry_after": retry_seconds} if retry_seconds else None,
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
                error_data.get("message", "Authentication failed"), error_data
            )
        elif status_code == 403:
            raise SideShiftForbiddenError(error_data.get("message", "Access forbidden"), error_data)
        elif status_code == 404:
            raise SideShiftNotFoundError(
                error_data.get("message", "Resource not found"), error_data
            )
        else:
            raise SideShiftAPIError(
                error_data.get("message", f"API error: {status_code}"),
                status_code,
                error_data,
            )


class SideShiftClient(BaseClient):
    """Synchronous client for SideShift API."""

    def __init__(
        self,
        secret: str | None = None,
        affiliate_id: str | None = None,
        user_ip: str | None = None,
        base_url: str | None = None,
        timeout: int | None = None,
        max_connections: int | None = None,
        max_keepalive_connections: int | None = None,
        enable_logging: bool = False,
        log_level: int | str | None = None,
    ):
        """Initialize synchronous client.

        Args:
            secret: SideShift account secret
            affiliate_id: Affiliate ID
            user_ip: End-user IP address
            base_url: Base URL for API (can also be set via SIDESHIFT_BASE_URL env var)
            timeout: Request timeout in seconds (can also be set via SIDESHIFT_TIMEOUT env var)
            max_connections: Maximum number of connections in pool (can also be set via SIDESHIFT_MAX_CONNECTIONS env var)
            max_keepalive_connections: Maximum number of keepalive connections (can also be set via SIDESHIFT_MAX_KEEPALIVE_CONNECTIONS env var)
            enable_logging: Whether to enable logging (default: False)
            log_level: Logging level if enable_logging is True (default: logging.INFO)
        """
        super().__init__(secret, affiliate_id, user_ip, base_url, enable_logging, log_level)
        self.timeout = SDKConfig.get_timeout(timeout)
        self.max_connections = SDKConfig.get_max_connections(max_connections)
        self.max_keepalive_connections = SDKConfig.get_max_keepalive_connections(max_keepalive_connections)
        
        # Configure connection pooling
        self._session = requests.Session()
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
            max_retries: Maximum number of retries for rate limits (can also be set via SIDESHIFT_MAX_RETRIES env var)

        Returns:
            Response JSON data
        """
        max_retries = SDKConfig.get_max_retries(max_retries)
        url = f"{self.base_url}{endpoint}"
        request_headers = self._get_headers(
            include_secret=require_auth, include_user_ip=require_user_ip
        )
        if headers:
            request_headers.update(headers)

        for attempt in range(max_retries + 1):
            try:
                if self._enable_logging:
                    self._logger.debug(
                        f"Request: {method} {endpoint} (attempt {attempt + 1}/{max_retries + 1})"
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
                    timeout=self.timeout,
                )

                if self._enable_logging:
                    self._logger.debug(f"Response: {method} {endpoint} - {response.status_code}")

                response_data = self._handle_response(response)
                
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
                        f"Rate limit exceeded for {method} {endpoint} (attempt {attempt + 1}/{max_retries + 1})"
                    )
                if attempt < max_retries:
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
                    self._logger.error(f"Network error for {method} {endpoint}: {error_msg}")
                network_error = SideShiftNetworkError(error_msg)
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
                    self._logger.error(f"Request exception for {method} {endpoint}: {str(e)}")
                network_error = SideShiftNetworkError(f"Network request failed: {str(e)}")
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
    ) -> JsonDict:
        """Make GET request.

        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            require_auth: Whether authentication is required
            require_user_ip: Whether user IP header is required

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
        )

    def post(
        self,
        endpoint: str,
        json_data: JsonDict | None = None,
        headers: HeadersDict | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
    ) -> JsonDict:
        """Make POST request.

        Args:
            endpoint: API endpoint
            json_data: JSON body data
            headers: Additional headers
            require_auth: Whether authentication is required
            require_user_ip: Whether user IP header is required

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
        )

    def get_binary(
        self,
        endpoint: str,
        headers: HeadersDict | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
    ) -> bytes:
        """Make GET request and return binary response.

        Args:
            endpoint: API endpoint
            headers: Additional headers
            require_auth: Whether authentication is required
            require_user_ip: Whether user IP header is required

        Returns:
            Response binary data
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = self._get_headers(
            include_secret=require_auth, include_user_ip=require_user_ip
        )
        if headers:
            request_headers.update(headers)

        response = self._session.get(
            url,
            headers=request_headers,
            timeout=self.timeout,
        )

        if response.status_code != 200:
            self._handle_response(response)
            return b""

        return response.content

    def close(self) -> None:
        """Close the session."""
        self._session.close()

    def __enter__(self) -> "SideShiftClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()


class AsyncSideShiftClient(BaseClient):
    """Asynchronous client for SideShift API."""

    def __init__(
        self,
        secret: str | None = None,
        affiliate_id: str | None = None,
        user_ip: str | None = None,
        base_url: str | None = None,
        timeout: int | None = None,
        max_connections: int | None = None,
        max_keepalive_connections: int | None = None,
        enable_logging: bool = False,
        log_level: int | str | None = None,
    ):
        """Initialize asynchronous client.

        Args:
            secret: SideShift account secret
            affiliate_id: Affiliate ID
            user_ip: End-user IP address
            base_url: Base URL for API (can also be set via SIDESHIFT_BASE_URL env var)
            timeout: Request timeout in seconds (can also be set via SIDESHIFT_TIMEOUT env var)
            max_connections: Maximum number of connections in pool (can also be set via SIDESHIFT_MAX_CONNECTIONS env var)
            max_keepalive_connections: Maximum number of keepalive connections (can also be set via SIDESHIFT_MAX_KEEPALIVE_CONNECTIONS env var)
            enable_logging: Whether to enable logging (default: False)
            log_level: Logging level if enable_logging is True (default: logging.INFO)
        """
        super().__init__(secret, affiliate_id, user_ip, base_url, enable_logging, log_level)
        self.timeout = SDKConfig.get_timeout(timeout)
        self.max_connections = SDKConfig.get_max_connections(max_connections)
        self.max_keepalive_connections = SDKConfig.get_max_keepalive_connections(max_keepalive_connections)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client.

        Returns:
            Async HTTP client
        """
        if self._client is None:
            limits = httpx.Limits(
                max_connections=self.max_connections,
                max_keepalive_connections=self.max_keepalive_connections,
            )
            self._client = httpx.AsyncClient(timeout=self.timeout, limits=limits)
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
            max_retries: Maximum number of retries for rate limits (can also be set via SIDESHIFT_MAX_RETRIES env var)

        Returns:
            Response JSON data
        """
        max_retries = SDKConfig.get_max_retries(max_retries)
        url = f"{self.base_url}{endpoint}"
        request_headers = self._get_headers(
            include_secret=require_auth, include_user_ip=require_user_ip
        )
        if headers:
            request_headers.update(headers)

        client = await self._get_client()

        for attempt in range(max_retries + 1):
            try:
                if self._enable_logging:
                    self._logger.debug(
                        f"Request: {method} {endpoint} (attempt {attempt + 1}/{max_retries + 1})"
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
                    timeout=self.timeout,
                )

                if self._enable_logging:
                    self._logger.debug(f"Response: {method} {endpoint} - {response.status_code}")

                response_data = self._handle_response(response)
                
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
                        f"Rate limit exceeded for {method} {endpoint} (attempt {attempt + 1}/{max_retries + 1})"
                    )
                if attempt < max_retries:
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
                    self._logger.error(f"Network error for {method} {endpoint}: {error_msg}")
                network_error = SideShiftNetworkError(error_msg)
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
            except httpx.RequestError as e:
                # Other httpx request exceptions (DNS, SSL, etc.)
                if self._enable_logging:
                    self._logger.error(f"Request exception for {method} {endpoint}: {str(e)}")
                network_error = SideShiftNetworkError(f"Network request failed: {str(e)}")
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
    ) -> JsonDict:
        """Make GET request.

        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            require_auth: Whether authentication is required
            require_user_ip: Whether user IP header is required

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
        )

    async def get_binary(
        self,
        endpoint: str,
        headers: HeadersDict | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
    ) -> bytes:
        """Make GET request and return binary response.

        Args:
            endpoint: API endpoint
            headers: Additional headers
            require_auth: Whether authentication is required
            require_user_ip: Whether user IP header is required

        Returns:
            Response binary data
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = self._get_headers(
            include_secret=require_auth, include_user_ip=require_user_ip
        )
        if headers:
            request_headers.update(headers)

        client = await self._get_client()
        response = await client.get(
            url,
            headers=request_headers,
            timeout=self.timeout,
        )

        if response.status_code != 200:
            self._handle_response(response)
            return b""

        return response.content

    async def post(
        self,
        endpoint: str,
        json_data: JsonDict | None = None,
        headers: HeadersDict | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
    ) -> JsonDict:
        """Make POST request.

        Args:
            endpoint: API endpoint
            json_data: JSON body data
            headers: Additional headers
            require_auth: Whether authentication is required
            require_user_ip: Whether user IP header is required

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
        )

    async def close(self) -> None:
        """Close the async client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "AsyncSideShiftClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
