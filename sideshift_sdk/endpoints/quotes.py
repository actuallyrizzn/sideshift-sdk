"""Quotes endpoints."""

from typing import TYPE_CHECKING

from sideshift_sdk.constants import HEADER_USER_IP
from sideshift_sdk.models import Quote, QuoteRequest
from sideshift_sdk.utils import validate_non_empty_string, validate_positive_amount

if TYPE_CHECKING:
    from sideshift_sdk.client import AsyncSideShiftClient, SideShiftClient


def request_quote(
    client: "SideShiftClient",
    deposit_coin: str,
    settle_coin: str,
    deposit_amount: str | None = None,
    settle_amount: str | None = None,
    deposit_network: str | None = None,
    settle_network: str | None = None,
    affiliate_id: str | None = None,
    commission_rate: str | None = None,
    user_ip: str | None = None,
) -> Quote:
    """Request a quote for a fixed rate shift.

    Args:
        client: SideShift client instance
        deposit_coin: Deposit coin ticker
        settle_coin: Settle coin ticker
        deposit_amount: Deposit amount (required if settle_amount is None)
        settle_amount: Settle amount (required if deposit_amount is None)
        deposit_network: Deposit network (required for non-native/multi-network tokens)
        settle_network: Settle network (required for non-native/multi-network tokens)
        affiliate_id: Affiliate ID (uses client default if not provided)
        commission_rate: Commission rate (optional, default 0.5%, max 2%)
        user_ip: End-user IP address (uses client default if not provided)

    Returns:
        Quote object

    Raises:
        ValueError: If both deposit_amount and settle_amount are None

    Examples:
        >>> client = SideShiftClient(secret="your-secret", affiliate_id="your-id")
        >>> quote = request_quote(
        ...     client,
        ...     deposit_coin="btc",
        ...     settle_coin="eth",
        ...     deposit_amount="0.1",
        ...     deposit_network="bitcoin",
        ...     settle_network="mainnet",
        ... )
        >>> print(f"Quote ID: {quote.id}, Rate: {quote.rate}")
    """
    if deposit_amount is None and settle_amount is None:
        raise ValueError("Either deposit_amount or settle_amount must be provided")

    request_data = QuoteRequest(
        deposit_coin=deposit_coin,
        deposit_network=deposit_network,
        settle_coin=settle_coin,
        settle_network=settle_network,
        deposit_amount=deposit_amount,
        settle_amount=settle_amount,
        affiliate_id=affiliate_id or client.affiliate_id or "",
        commission_rate=commission_rate,
    )

    headers = {}
    if user_ip or client.user_ip:
        headers[HEADER_USER_IP] = user_ip or client.user_ip or ""

    response = client.post(
        "/quotes",
        json_data=request_data.model_dump(by_alias=True, exclude_none=True),
        headers=headers,
        require_auth=True,
        require_user_ip=bool(user_ip or client.user_ip),
    )
    return Quote(**response)


async def request_quote_async(
    client: "AsyncSideShiftClient",
    deposit_coin: str,
    settle_coin: str,
    deposit_amount: str | None = None,
    settle_amount: str | None = None,
    deposit_network: str | None = None,
    settle_network: str | None = None,
    affiliate_id: str | None = None,
    commission_rate: str | None = None,
    user_ip: str | None = None,
) -> Quote:
    """Request a quote for a fixed rate shift (async).

    Args:
        client: Async SideShift client instance
        deposit_coin: Deposit coin ticker
        settle_coin: Settle coin ticker
        deposit_amount: Deposit amount (required if settle_amount is None)
        settle_amount: Settle amount (required if deposit_amount is None)
        deposit_network: Deposit network (required for non-native/multi-network tokens)
        settle_network: Settle network (required for non-native/multi-network tokens)
        affiliate_id: Affiliate ID (uses client default if not provided)
        commission_rate: Commission rate (optional, default 0.5%, max 2%)
        user_ip: End-user IP address (uses client default if not provided)

    Returns:
        Quote object

    Raises:
        ValueError: If both deposit_amount and settle_amount are None

    Examples:
        >>> async with AsyncSideShiftClient(secret="your-secret") as client:
        ...     quote = await request_quote_async(
        ...         client,
        ...         deposit_coin="btc",
        ...         settle_coin="eth",
        ...         deposit_amount="0.1",
        ...     )
        ...     print(f"Quote ID: {quote.id}")
    """
    # Input validation
    validate_non_empty_string(deposit_coin, "deposit_coin")
    validate_non_empty_string(settle_coin, "settle_coin")
    
    if deposit_amount is not None:
        validate_positive_amount(deposit_amount, "deposit_amount")
    if settle_amount is not None:
        validate_positive_amount(settle_amount, "settle_amount")
    
    if deposit_amount is None and settle_amount is None:
        raise ValueError("Either deposit_amount or settle_amount must be provided")

    request_data = QuoteRequest(
        deposit_coin=deposit_coin,
        deposit_network=deposit_network,
        settle_coin=settle_coin,
        settle_network=settle_network,
        deposit_amount=deposit_amount,
        settle_amount=settle_amount,
        affiliate_id=affiliate_id or client.affiliate_id or "",
        commission_rate=commission_rate,
    )

    headers = {}
    if user_ip or client.user_ip:
        headers[HEADER_USER_IP] = user_ip or client.user_ip or ""

    response = await client.post(
        "/quotes",
        json_data=request_data.model_dump(by_alias=True, exclude_none=True),
        headers=headers,
        require_auth=True,
        require_user_ip=bool(user_ip or client.user_ip),
    )
    return Quote(**response)
