"""Account endpoints."""

from typing import TYPE_CHECKING

from sideshift_sdk.models import Account, Permissions, XAIStats

if TYPE_CHECKING:
    from sideshift_sdk.client import AsyncSideShiftClient, SideShiftClient


def get_account(client: "SideShiftClient") -> Account:
    """Get account information.

    Args:
        client: SideShift client instance

    Returns:
        Account object
    """
    response = client.get("/account", require_auth=True)
    return Account(**response)


async def get_account_async(client: "AsyncSideShiftClient") -> Account:
    """Get account information (async).

    Args:
        client: Async SideShift client instance

    Returns:
        Account object
    """
    response = await client.get("/account", require_auth=True)
    return Account(**response)


def get_permissions(client: "SideShiftClient", user_ip: str | None = None) -> Permissions:
    """Get permissions for creating shifts.

    Args:
        client: SideShift client instance
        user_ip: End-user IP address (uses client default if not provided)

    Returns:
        Permissions object
    """
    headers = {}
    if user_ip or client.user_ip:
        headers["x-user-ip"] = user_ip or client.user_ip or ""

    response = client.get(
        "/permissions",
        headers=headers if headers else None,
        require_auth=False,
        require_user_ip=bool(user_ip or client.user_ip),
    )
    return Permissions(**response)


async def get_permissions_async(client: "AsyncSideShiftClient", user_ip: str | None = None) -> Permissions:
    """Get permissions for creating shifts (async).

    Args:
        client: Async SideShift client instance
        user_ip: End-user IP address (uses client default if not provided)

    Returns:
        Permissions object
    """
    headers = {}
    if user_ip or client.user_ip:
        headers["x-user-ip"] = user_ip or client.user_ip or ""

    response = await client.get(
        "/permissions",
        headers=headers if headers else None,
        require_auth=False,
        require_user_ip=bool(user_ip or client.user_ip),
    )
    return Permissions(**response)


def get_xai_stats(client: "SideShiftClient") -> XAIStats:
    """Get XAI coin statistics.

    Args:
        client: SideShift client instance

    Returns:
        XAIStats object
    """
    response = client.get("/xai/stats", require_auth=False)
    return XAIStats(**response)


async def get_xai_stats_async(client: "AsyncSideShiftClient") -> XAIStats:
    """Get XAI coin statistics (async).

    Args:
        client: Async SideShift client instance

    Returns:
        XAIStats object
    """
    response = await client.get("/xai/stats", require_auth=False)
    return XAIStats(**response)

