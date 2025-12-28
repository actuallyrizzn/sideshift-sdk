"""Configuration management for SideShift SDK."""

import os

from sideshift_sdk.constants import API_BASE_DOMAIN, BASE_URL, DEFAULT_API_VERSION, SUPPORTED_API_VERSIONS


class SDKConfig:
    """Configuration for SideShift SDK.

    This class manages all configurable values for the SDK, allowing them to be
    set via environment variables or passed directly to client constructors.
    """

    # Default values
    DEFAULT_TIMEOUT = 30
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_BASE_URL = BASE_URL
    DEFAULT_API_VERSION = DEFAULT_API_VERSION
    DEFAULT_MAX_CONNECTIONS = 10
    DEFAULT_MAX_KEEPALIVE_CONNECTIONS = 5
    DEFAULT_VERIFY_SSL = True
    # Size limits in bytes (10MB for requests, 50MB for responses)
    DEFAULT_MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    DEFAULT_MAX_RESPONSE_SIZE = 50 * 1024 * 1024  # 50MB

    @staticmethod
    def get_timeout(provided: int | None = None) -> int:
        """Get timeout value from provided value or environment variable.

        Args:
            provided: Timeout value provided directly (takes precedence)

        Returns:
            Timeout in seconds
        """
        if provided is not None:
            return provided
        env_timeout = os.getenv("SIDESHIFT_TIMEOUT")
        if env_timeout:
            try:
                return int(env_timeout)
            except ValueError:
                pass
        return SDKConfig.DEFAULT_TIMEOUT

    @staticmethod
    def get_max_retries(provided: int | None = None) -> int:
        """Get max retries value from provided value or environment variable.

        Args:
            provided: Max retries value provided directly (takes precedence)

        Returns:
            Maximum number of retries
        """
        if provided is not None:
            return provided
        env_retries = os.getenv("SIDESHIFT_MAX_RETRIES")
        if env_retries:
            try:
                return int(env_retries)
            except ValueError:
                pass
        return SDKConfig.DEFAULT_MAX_RETRIES

    @staticmethod
    def get_api_version(provided: str | None = None) -> str:
        """Get API version from provided value or environment variable.

        Args:
            provided: API version provided directly (takes precedence)

        Returns:
            API version string (e.g., "v2")

        Raises:
            ValueError: If the provided version is not supported
        """
        if provided is not None:
            if provided not in SUPPORTED_API_VERSIONS:
                raise ValueError(
                    f"Unsupported API version: {provided}. "
                    f"Supported versions: {', '.join(SUPPORTED_API_VERSIONS)}"
                )
            return provided
        env_version = os.getenv("SIDESHIFT_API_VERSION")
        if env_version:
            if env_version not in SUPPORTED_API_VERSIONS:
                raise ValueError(
                    f"Unsupported API version from environment: {env_version}. "
                    f"Supported versions: {', '.join(SUPPORTED_API_VERSIONS)}"
                )
            return env_version
        return SDKConfig.DEFAULT_API_VERSION

    @staticmethod
    def get_base_url(provided: str | None = None, api_version: str | None = None) -> str:
        """Get base URL from provided value, API version, or environment variable.

        Args:
            provided: Base URL provided directly (takes precedence)
            api_version: API version to use when constructing base URL

        Returns:
            Base URL for API
        """
        if provided is not None:
            return provided
        env_url = os.getenv("SIDESHIFT_BASE_URL")
        if env_url:
            return env_url
        # Construct base URL from domain and API version
        if api_version is not None:
            validated_version = SDKConfig.get_api_version(api_version)
            return f"{API_BASE_DOMAIN}/api/{validated_version}"
        return SDKConfig.DEFAULT_BASE_URL

    @staticmethod
    def get_max_connections(provided: int | None = None) -> int:
        """Get max connections value from provided value or environment variable.

        Args:
            provided: Max connections value provided directly (takes precedence)

        Returns:
            Maximum number of connections in pool
        """
        if provided is not None:
            return provided
        env_connections = os.getenv("SIDESHIFT_MAX_CONNECTIONS")
        if env_connections:
            try:
                return int(env_connections)
            except ValueError:
                pass
        return SDKConfig.DEFAULT_MAX_CONNECTIONS

    @staticmethod
    def get_max_keepalive_connections(provided: int | None = None) -> int:
        """Get max keepalive connections value from provided value or environment variable.

        Args:
            provided: Max keepalive connections value provided directly (takes precedence)

        Returns:
            Maximum number of keepalive connections in pool
        """
        if provided is not None:
            return provided
        env_keepalive = os.getenv("SIDESHIFT_MAX_KEEPALIVE_CONNECTIONS")
        if env_keepalive:
            try:
                return int(env_keepalive)
            except ValueError:
                pass
        return SDKConfig.DEFAULT_MAX_KEEPALIVE_CONNECTIONS

    @staticmethod
    def get_proxy(provided: str | dict[str, str] | None = None) -> str | dict[str, str] | None:
        """Get proxy value from provided value or environment variable.

        Args:
            provided: Proxy value provided directly (takes precedence).
                     Can be a string URL or dict mapping protocol to URL.

        Returns:
            Proxy configuration (string URL, dict, or None)
        """
        if provided is not None:
            return provided
        env_proxy = os.getenv("SIDESHIFT_PROXY")
        if env_proxy:
            return env_proxy
        # Also check standard HTTP_PROXY and HTTPS_PROXY
        http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
        https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
        if http_proxy or https_proxy:
            proxies = {}
            if http_proxy:
                proxies["http"] = http_proxy
            if https_proxy:
                proxies["https"] = https_proxy
            return proxies
        return None

    @staticmethod
    def get_verify_ssl(provided: bool | None = None) -> bool:
        """Get SSL verification value from provided value or environment variable.

        Args:
            provided: SSL verification value provided directly (takes precedence)

        Returns:
            Whether to verify SSL certificates (True by default for security)
        """
        if provided is not None:
            return provided
        env_verify = os.getenv("SIDESHIFT_VERIFY_SSL")
        if env_verify:
            # Accept "true", "1", "yes" as True, everything else as False
            return env_verify.lower() in ("true", "1", "yes")
        return SDKConfig.DEFAULT_VERIFY_SSL

    @staticmethod
    def get_max_request_size(provided: int | None = None) -> int:
        """Get max request size value from provided value or environment variable.

        Args:
            provided: Max request size value provided directly (takes precedence)

        Returns:
            Maximum request body size in bytes
        """
        if provided is not None:
            return provided
        env_size = os.getenv("SIDESHIFT_MAX_REQUEST_SIZE")
        if env_size:
            try:
                return int(env_size)
            except ValueError:
                pass
        return SDKConfig.DEFAULT_MAX_REQUEST_SIZE

    @staticmethod
    def get_max_response_size(provided: int | None = None) -> int:
        """Get max response size value from provided value or environment variable.

        Args:
            provided: Max response size value provided directly (takes precedence)

        Returns:
            Maximum response body size in bytes
        """
        if provided is not None:
            return provided
        env_size = os.getenv("SIDESHIFT_MAX_RESPONSE_SIZE")
        if env_size:
            try:
                return int(env_size)
            except ValueError:
                pass
        return SDKConfig.DEFAULT_MAX_RESPONSE_SIZE

