"""Client classes for SideShift SDK."""

import os
import time
from typing import Any

import httpx
import requests
from pydantic import BaseModel

from sideshift_sdk.exceptions import (
    SideShiftAPIError,
    SideShiftAuthenticationError,
    SideShiftException,
    SideShiftForbiddenError,
    SideShiftNotFoundError,
    SideShiftRateLimitError,
)
from sideshift_sdk.utils import exponential_backoff


class BaseClient:
    """Base client with common functionality."""

    BASE_URL = "https://sideshift.ai/api/v2"

    def __init__(
        self,
        secret: str | None = None,
        affiliate_id: str | None = None,
        user_ip: str | None = None,
        base_url: str | None = None,
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
        """
        self.secret = secret or os.getenv("SIDESHIFT_SECRET")
        self.affiliate_id = affiliate_id or os.getenv("AFFILIATE_ID")
        self.user_ip = user_ip or os.getenv("SIDESHIFT_USER_IP")
        self.base_url = base_url or self.BASE_URL

    def _get_headers(self, include_secret: bool = False, include_user_ip: bool = False) -> dict[str, str]:
        """Get request headers.

        Args:
            include_secret: Whether to include x-sideshift-secret header
            include_user_ip: Whether to include x-user-ip header

        Returns:
            Headers dictionary
        """
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        if include_secret and self.secret:
            headers["x-sideshift-secret"] = self.secret

        if include_user_ip and self.user_ip:
            headers["x-user-ip"] = self.user_ip

        return headers

    def _handle_response(self, response: requests.Response | httpx.Response) -> dict[str, Any]:
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
            except Exception:
                return {}

        # Handle rate limiting
        if status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise SideShiftRateLimitError(
                "Rate limit exceeded",
                response_data={"retry_after": retry_seconds} if retry_seconds else None,
            )

        # Handle other errors
        try:
            error_data = response.json()
        except Exception:
            # Handle both requests and httpx response types
            if hasattr(response, "text"):
                error_text = response.text
            elif hasattr(response, "content"):
                try:
                    error_text = response.content.decode("utf-8")
                except Exception:
                    error_text = "Unknown error"
            else:
                error_text = "Unknown error"
            error_data = {"message": error_text or "Unknown error"}

        if status_code == 401:
            raise SideShiftAuthenticationError(error_data.get("message", "Authentication failed"), error_data)
        elif status_code == 403:
            raise SideShiftForbiddenError(error_data.get("message", "Access forbidden"), error_data)
        elif status_code == 404:
            raise SideShiftNotFoundError(error_data.get("message", "Resource not found"), error_data)
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
        timeout: int = 30,
    ):
        """Initialize synchronous client.

        Args:
            secret: SideShift account secret
            affiliate_id: Affiliate ID
            user_ip: End-user IP address
            base_url: Base URL for API
            timeout: Request timeout in seconds
        """
        super().__init__(secret, affiliate_id, user_ip, base_url)
        self.timeout = timeout
        self._session = requests.Session()

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json_data: JSON body data
            headers: Additional headers
            require_auth: Whether authentication is required
            require_user_ip: Whether user IP header is required
            max_retries: Maximum number of retries for rate limits

        Returns:
            Response JSON data
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = self._get_headers(include_secret=require_auth, include_user_ip=require_user_ip)
        if headers:
            request_headers.update(headers)

        for attempt in range(max_retries + 1):
            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=request_headers,
                    timeout=self.timeout,
                )

                return self._handle_response(response)

            except SideShiftRateLimitError as e:
                if attempt < max_retries:
                    wait_time = exponential_backoff(attempt)
                    time.sleep(wait_time)
                    continue
                raise

        raise SideShiftException("Max retries exceeded")

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
    ) -> dict[str, Any]:
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
        return self._request("GET", endpoint, params=params, headers=headers, require_auth=require_auth, require_user_ip=require_user_ip)

    def post(
        self,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
    ) -> dict[str, Any]:
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
        return self._request("POST", endpoint, json_data=json_data, headers=headers, require_auth=require_auth, require_user_ip=require_user_ip)

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
        timeout: int = 30,
    ):
        """Initialize asynchronous client.

        Args:
            secret: SideShift account secret
            affiliate_id: Affiliate ID
            user_ip: End-user IP address
            base_url: Base URL for API
            timeout: Request timeout in seconds
        """
        super().__init__(secret, affiliate_id, user_ip, base_url)
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client.

        Returns:
            Async HTTP client
        """
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json_data: JSON body data
            headers: Additional headers
            require_auth: Whether authentication is required
            require_user_ip: Whether user IP header is required
            max_retries: Maximum number of retries for rate limits

        Returns:
            Response JSON data
        """
        import asyncio

        url = f"{self.base_url}{endpoint}"
        request_headers = self._get_headers(include_secret=require_auth, include_user_ip=require_user_ip)
        if headers:
            request_headers.update(headers)

        client = await self._get_client()

        for attempt in range(max_retries + 1):
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=request_headers,
                )

                return self._handle_response(response)

            except SideShiftRateLimitError as e:
                if attempt < max_retries:
                    wait_time = exponential_backoff(attempt)
                    await asyncio.sleep(wait_time)
                    continue
                raise

        raise SideShiftException("Max retries exceeded")

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
    ) -> dict[str, Any]:
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
        return await self._request("GET", endpoint, params=params, headers=headers, require_auth=require_auth, require_user_ip=require_user_ip)

    async def post(
        self,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        require_auth: bool = False,
        require_user_ip: bool = False,
    ) -> dict[str, Any]:
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
        return await self._request("POST", endpoint, json_data=json_data, headers=headers, require_auth=require_auth, require_user_ip=require_user_ip)

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

