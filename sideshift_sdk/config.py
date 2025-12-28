"""Configuration management for SideShift SDK."""

import os
from typing import Optional

from sideshift_sdk.constants import BASE_URL


class SDKConfig:
    """Configuration for SideShift SDK.

    This class manages all configurable values for the SDK, allowing them to be
    set via environment variables or passed directly to client constructors.
    """

    # Default values
    DEFAULT_TIMEOUT = 30
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_BASE_URL = BASE_URL
    DEFAULT_MAX_CONNECTIONS = 10
    DEFAULT_MAX_KEEPALIVE_CONNECTIONS = 5
    DEFAULT_VERIFY_SSL = True

    @staticmethod
    def get_timeout(provided: Optional[int] = None) -> int:
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
    def get_max_retries(provided: Optional[int] = None) -> int:
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
    def get_base_url(provided: Optional[str] = None) -> str:
        """Get base URL from provided value or environment variable.

        Args:
            provided: Base URL provided directly (takes precedence)

        Returns:
            Base URL for API
        """
        if provided is not None:
            return provided
        env_url = os.getenv("SIDESHIFT_BASE_URL")
        if env_url:
            return env_url
        return SDKConfig.DEFAULT_BASE_URL

    @staticmethod
    def get_max_connections(provided: Optional[int] = None) -> int:
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
    def get_max_keepalive_connections(provided: Optional[int] = None) -> int:
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
    def get_verify_ssl(provided: Optional[bool] = None) -> bool:
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

