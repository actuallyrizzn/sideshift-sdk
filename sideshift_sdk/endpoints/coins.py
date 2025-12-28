"""Coins endpoints."""

from typing import TYPE_CHECKING

from sideshift_sdk.constants import HEADER_ACCEPT, IMAGE_FORMAT_PNG, IMAGE_FORMAT_SVG
from sideshift_sdk.models import Coin

if TYPE_CHECKING:
    from sideshift_sdk.client import AsyncSideShiftClient, SideShiftClient


def get_coins(client: "SideShiftClient") -> list[Coin]:
    """Get list of all available coins and networks.

    Args:
        client: SideShift client instance

    Returns:
        List of Coin objects

    Examples:
        >>> client = SideShiftClient()
        >>> coins_list = get_coins(client)
        >>> print(f"Available coins: {len(coins_list)}")
        >>> for coin in coins_list[:5]:
        ...     print(f"{coin.coin} on {coin.networks}")
    """
    response = client.get("/coins", require_auth=False)
    return [Coin(**coin_data) for coin_data in response]


async def get_coins_async(client: "AsyncSideShiftClient") -> list[Coin]:
    """Get list of all available coins and networks (async).

    Args:
        client: Async SideShift client instance

    Returns:
        List of Coin objects
    """
    response = await client.get("/coins", require_auth=False)
    return [Coin(**coin_data) for coin_data in response]


def get_coin_icon(
    client: "SideShiftClient",
    coin_network: str,
    format: str = "svg",  # noqa: A002
) -> bytes:
    """Get coin icon.

    Args:
        client: SideShift client instance
        coin_network: Coin-network identifier (e.g., 'btc-bitcoin', 'btc-mainnet', 'btc')
        format: Image format ('svg' or 'png')

    Returns:
        Icon image bytes
    """
    accept_header = f"image/{format}+xml" if format == IMAGE_FORMAT_SVG else f"image/{format}"
    headers = {HEADER_ACCEPT: accept_header}

    response = client._session.get(
        f"{client.base_url}/coins/icon/{coin_network}",
        headers=headers,
        timeout=client.timeout,
    )

    if response.status_code != 200:
        client._handle_response(response)
        return b""  # Should not reach here, but satisfy type checker

    return response.content


async def get_coin_icon_async(
    client: "AsyncSideShiftClient",
    coin_network: str,
    format: str = "svg",  # noqa: A002
) -> bytes:
    """Get coin icon (async).

    Args:
        client: Async SideShift client instance
        coin_network: Coin-network identifier (e.g., 'btc-bitcoin', 'btc-mainnet', 'btc')
        format: Image format ('svg' or 'png')

    Returns:
        Icon image bytes
    """
    accept_header = f"image/{format}+xml" if format == IMAGE_FORMAT_SVG else f"image/{format}"
    headers = {HEADER_ACCEPT: accept_header}

    httpx_client = await client._get_client()
    response = await httpx_client.get(
        f"{client.base_url}/coins/icon/{coin_network}",
        headers=headers,
    )

    if response.status_code != 200:
        client._handle_response(response)
        return b""  # Should not reach here, but satisfy type checker

    return response.content
