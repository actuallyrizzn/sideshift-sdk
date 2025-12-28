"""Coins endpoints."""

from typing import TYPE_CHECKING

from sideshift_sdk.constants import HEADER_ACCEPT, IMAGE_FORMAT_PNG, IMAGE_FORMAT_SVG
from sideshift_sdk.models import Coin
from sideshift_sdk.utils import validate_non_empty_string

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

    return client.get_binary(
        f"/coins/icon/{coin_network}",
        headers=headers,
        require_auth=False,
    )


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
    # Input validation
    validate_non_empty_string(coin_network, "coin_network")
    if format not in (IMAGE_FORMAT_SVG, IMAGE_FORMAT_PNG):
        raise ValueError(f"format must be '{IMAGE_FORMAT_SVG}' or '{IMAGE_FORMAT_PNG}', got '{format}'")
    
    accept_header = f"image/{format}+xml" if format == IMAGE_FORMAT_SVG else f"image/{format}"
    headers = {HEADER_ACCEPT: accept_header}

    return await client.get_binary(
        f"/coins/icon/{coin_network}",
        headers=headers,
        require_auth=False,
    )
