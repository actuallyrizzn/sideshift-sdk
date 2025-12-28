"""Checkout endpoints."""

from typing import TYPE_CHECKING

from sideshift_sdk.constants import HEADER_USER_IP
from sideshift_sdk.models import Checkout, CheckoutRequest
from sideshift_sdk.utils import normalize_affiliate_id

if TYPE_CHECKING:
    from sideshift_sdk.client import AsyncSideShiftClient, SideShiftClient


def get_checkout(client: "SideShiftClient", checkout_id: str) -> Checkout:
    """Get checkout information.

    Args:
        client: SideShift client instance
        checkout_id: Unique checkout identifier

    Returns:
        Checkout object
    """
    response = client.get(f"/checkout/{checkout_id}", require_auth=False)
    return Checkout(**response)


async def get_checkout_async(client: "AsyncSideShiftClient", checkout_id: str) -> Checkout:
    """Get checkout information (async).

    Args:
        client: Async SideShift client instance
        checkout_id: Unique checkout identifier

    Returns:
        Checkout object
    """
    response = await client.get(f"/checkout/{checkout_id}", require_auth=False)
    return Checkout(**response)


def create_checkout(
    client: "SideShiftClient",
    settle_coin: str,
    settle_network: str,
    settle_amount: str,
    settle_address: str,
    affiliate_id: str,
    success_url: str,
    cancel_url: str,
    settle_memo: str | None = None,
    user_ip: str | None = None,
) -> Checkout:
    """Create a checkout.

    Args:
        client: SideShift client instance
        settle_coin: Settle coin ticker
        settle_network: Settle network identifier
        settle_amount: Settle amount
        settle_address: Address to receive the settle coin
        affiliate_id: Affiliate ID (uses client default if not provided)
        success_url: URL to redirect on success
        cancel_url: URL to redirect on cancel
        settle_memo: Memo for coins that require it (optional)
        user_ip: End-user IP address (required, uses client default if not provided)

    Returns:
        Checkout object

    Examples:
        >>> client = SideShiftClient(secret="your-secret", user_ip="1.2.3.4")
        >>> checkout = create_checkout(
        ...     client,
        ...     settle_coin="eth",
        ...     settle_network="mainnet",
        ...     settle_amount="1.0",
        ...     settle_address="0x...",
        ...     affiliate_id="your-id",
        ...     success_url="https://example.com/success",
        ...     cancel_url="https://example.com/cancel",
        ... )
        >>> print(f"Checkout URL: {checkout.checkout_url}")
    """
    request_data = CheckoutRequest(
        settle_coin=settle_coin,
        settle_network=settle_network,
        settle_amount=settle_amount,
        settle_address=settle_address,
        settle_memo=settle_memo,
        affiliate_id=normalize_affiliate_id(affiliate_id) or normalize_affiliate_id(client.affiliate_id) or "",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    headers = {}
    if user_ip or client.user_ip:
        headers[HEADER_USER_IP] = user_ip or client.user_ip or ""

    if not (user_ip or client.user_ip):
        raise ValueError(
            "user_ip is required for create_checkout (or set via client/user_ip parameter)"
        )

    response = client.post(
        "/checkout",
        json_data=request_data.model_dump(by_alias=True, exclude_none=True),
        headers=headers,
        require_auth=True,
        require_user_ip=True,
    )
    return Checkout(**response)


async def create_checkout_async(
    client: "AsyncSideShiftClient",
    settle_coin: str,
    settle_network: str,
    settle_amount: str,
    settle_address: str,
    affiliate_id: str,
    success_url: str,
    cancel_url: str,
    settle_memo: str | None = None,
    user_ip: str | None = None,
) -> Checkout:
    """Create a checkout (async).

    Args:
        client: Async SideShift client instance
        settle_coin: Settle coin ticker
        settle_network: Settle network identifier
        settle_amount: Settle amount
        settle_address: Address to receive the settle coin
        affiliate_id: Affiliate ID (uses client default if not provided)
        success_url: URL to redirect on success
        cancel_url: URL to redirect on cancel
        settle_memo: Memo for coins that require it (optional)
        user_ip: End-user IP address (required, uses client default if not provided)

    Returns:
        Checkout object
    """
    request_data = CheckoutRequest(
        settle_coin=settle_coin,
        settle_network=settle_network,
        settle_amount=settle_amount,
        settle_address=settle_address,
        settle_memo=settle_memo,
        affiliate_id=normalize_affiliate_id(affiliate_id) or normalize_affiliate_id(client.affiliate_id) or "",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    headers = {}
    if user_ip or client.user_ip:
        headers[HEADER_USER_IP] = user_ip or client.user_ip or ""

    if not (user_ip or client.user_ip):
        raise ValueError(
            "user_ip is required for create_checkout (or set via client/user_ip parameter)"
        )

    response = await client.post(
        "/checkout",
        json_data=request_data.model_dump(by_alias=True, exclude_none=True),
        headers=headers,
        require_auth=True,
        require_user_ip=True,
    )
    return Checkout(**response)
