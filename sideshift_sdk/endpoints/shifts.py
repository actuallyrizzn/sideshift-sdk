"""Shifts endpoints."""

from typing import TYPE_CHECKING

from sideshift_sdk.constants import HEADER_USER_IP
from sideshift_sdk.models import (
    CancelOrderRequest,
    FixedShiftRequest,
    RecentShift,
    SetRefundAddressRequest,
    Shift,
    VariableShiftRequest,
)
from sideshift_sdk.utils import validate_non_empty_string

if TYPE_CHECKING:
    from sideshift_sdk.client import AsyncSideShiftClient, SideShiftClient


def get_shift(client: "SideShiftClient", shift_id: str) -> Shift:
    """Get shift information.

    Args:
        client: SideShift client instance
        shift_id: Unique shift identifier

    Returns:
        Shift object

    Examples:
        >>> client = SideShiftClient()
        >>> shift = get_shift(client, shift_id="your-shift-id")
        >>> print(f"Status: {shift.status}, Deposit: {shift.deposit_address}")
    """
    response = client.get(f"/shifts/{shift_id}", require_auth=False)
    return Shift(**response)


async def get_shift_async(client: "AsyncSideShiftClient", shift_id: str) -> Shift:
    """Get shift information (async).

    Args:
        client: Async SideShift client instance
        shift_id: Unique shift identifier

    Returns:
        Shift object
    """
    response = await client.get(f"/shifts/{shift_id}", require_auth=False)
    return Shift(**response)


def get_bulk_shifts(client: "SideShiftClient", shift_ids: list[str]) -> list[Shift]:
    """Get multiple shifts.

    Args:
        client: SideShift client instance
        shift_ids: List of shift IDs

    Returns:
        List of Shift objects
    """
    params = {"ids": ",".join(shift_ids)}
    response = client.get("/shifts", params=params, require_auth=False)
    return [Shift(**shift_data) for shift_data in response]


async def get_bulk_shifts_async(
    client: "AsyncSideShiftClient", shift_ids: list[str]
) -> list[Shift]:
    """Get multiple shifts (async).

    Args:
        client: Async SideShift client instance
        shift_ids: List of shift IDs

    Returns:
        List of Shift objects
    """
    params = {"ids": ",".join(shift_ids)}
    response = await client.get("/shifts", params=params, require_auth=False)
    return [Shift(**shift_data) for shift_data in response]


def get_recent_shifts(client: "SideShiftClient", limit: int = 10) -> list[RecentShift]:
    """Get recent completed shifts.

    Args:
        client: SideShift client instance
        limit: Number of recent shifts to return (1-100, default: 10)

    Returns:
        List of RecentShift objects
    """
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")

    params = {"limit": limit}
    response = client.get("/recent-shifts", params=params, require_auth=False)
    return [RecentShift(**shift_data) for shift_data in response]


async def get_recent_shifts_async(
    client: "AsyncSideShiftClient", limit: int = 10
) -> list[RecentShift]:
    """Get recent completed shifts (async).

    Args:
        client: Async SideShift client instance
        limit: Number of recent shifts to return (1-100, default: 10)

    Returns:
        List of RecentShift objects
    """
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")

    params = {"limit": limit}
    response = await client.get("/recent-shifts", params=params, require_auth=False)
    return [RecentShift(**shift_data) for shift_data in response]


def create_fixed_shift(
    client: "SideShiftClient",
    quote_id: str,
    settle_address: str,
    affiliate_id: str | None = None,
    settle_memo: str | None = None,
    refund_address: str | None = None,
    refund_memo: str | None = None,
    external_id: str | None = None,
    user_ip: str | None = None,
) -> Shift:
    """Create a fixed rate shift.

    Args:
        client: SideShift client instance
        quote_id: Quote ID from request_quote()
        settle_address: Address to receive the settle coin
        affiliate_id: Affiliate ID (must match quote, uses client default if not provided)
        settle_memo: Memo for coins that require it
        refund_address: Refund address (optional)
        refund_memo: Refund memo (optional)
        external_id: Integration's own ID (optional)
        user_ip: End-user IP address (uses client default if not provided)

    Returns:
        Shift object

    Examples:
        >>> client = SideShiftClient(secret="your-secret", affiliate_id="your-id")
        >>> quote = request_quote(client, "btc", "eth", deposit_amount="0.1")
        >>> shift = create_fixed_shift(
        ...     client,
        ...     quote_id=quote.id,
        ...     settle_address="0x...",
        ... )
        >>> print(f"Shift ID: {shift.id}, Deposit Address: {shift.deposit_address}")
    """
    # Input validation
    validate_non_empty_string(quote_id, "quote_id")
    validate_non_empty_string(settle_address, "settle_address")

    request_data = FixedShiftRequest(
        settle_address=settle_address,
        settle_memo=settle_memo,
        affiliate_id=affiliate_id or client.affiliate_id or "",
        quote_id=quote_id,
        refund_address=refund_address,
        refund_memo=refund_memo,
        external_id=external_id,
    )

    headers = {}
    if user_ip or client.user_ip:
        headers[HEADER_USER_IP] = user_ip or client.user_ip or ""

    response = client.post(
        "/shifts/fixed",
        json_data=request_data.model_dump(by_alias=True, exclude_none=True),
        headers=headers,
        require_auth=True,
        require_user_ip=bool(user_ip or client.user_ip),
    )
    return Shift(**response)


async def create_fixed_shift_async(
    client: "AsyncSideShiftClient",
    quote_id: str,
    settle_address: str,
    affiliate_id: str | None = None,
    settle_memo: str | None = None,
    refund_address: str | None = None,
    refund_memo: str | None = None,
    external_id: str | None = None,
    user_ip: str | None = None,
) -> Shift:
    """Create a fixed rate shift (async).

    Args:
        client: Async SideShift client instance
        quote_id: Quote ID from request_quote()
        settle_address: Address to receive the settle coin
        affiliate_id: Affiliate ID (must match quote, uses client default if not provided)
        settle_memo: Memo for coins that require it
        refund_address: Refund address (optional)
        refund_memo: Refund memo (optional)
        external_id: Integration's own ID (optional)
        user_ip: End-user IP address (uses client default if not provided)

    Returns:
        Shift object
    """
    # Input validation
    validate_non_empty_string(quote_id, "quote_id")
    validate_non_empty_string(settle_address, "settle_address")

    request_data = FixedShiftRequest(
        settle_address=settle_address,
        settle_memo=settle_memo,
        affiliate_id=affiliate_id or client.affiliate_id or "",
        quote_id=quote_id,
        refund_address=refund_address,
        refund_memo=refund_memo,
        external_id=external_id,
    )

    headers = {}
    if user_ip or client.user_ip:
        headers[HEADER_USER_IP] = user_ip or client.user_ip or ""

    response = await client.post(
        "/shifts/fixed",
        json_data=request_data.model_dump(by_alias=True, exclude_none=True),
        headers=headers,
        require_auth=True,
        require_user_ip=bool(user_ip or client.user_ip),
    )
    return Shift(**response)


def create_variable_shift(
    client: "SideShiftClient",
    deposit_coin: str,
    settle_coin: str,
    settle_address: str,
    deposit_network: str | None = None,
    settle_network: str | None = None,
    affiliate_id: str | None = None,
    settle_memo: str | None = None,
    refund_address: str | None = None,
    refund_memo: str | None = None,
    external_id: str | None = None,
    user_ip: str | None = None,
) -> Shift:
    """Create a variable rate shift.

    Args:
        client: SideShift client instance
        deposit_coin: Deposit coin ticker
        settle_coin: Settle coin ticker
        settle_address: Address to receive the settle coin
        deposit_network: Deposit network (required for non-native/multi-network tokens)
        settle_network: Settle network (required for non-native/multi-network tokens)
        affiliate_id: Affiliate ID (uses client default if not provided)
        settle_memo: Memo for coins that require it
        refund_address: Refund address (optional)
        refund_memo: Refund memo (optional)
        external_id: Integration's own ID (optional)
        user_ip: End-user IP address (uses client default if not provided)

    Returns:
        Shift object

    Examples:
        >>> client = SideShiftClient(secret="your-secret", affiliate_id="your-id")
        >>> shift = create_variable_shift(
        ...     client,
        ...     deposit_coin="btc",
        ...     settle_coin="eth",
        ...     settle_address="0x...",
        ...     deposit_network="bitcoin",
        ...     settle_network="mainnet",
        ... )
        >>> print(f"Variable shift created: {shift.id}")
    """
    request_data = VariableShiftRequest(
        deposit_coin=deposit_coin,
        deposit_network=deposit_network,
        settle_coin=settle_coin,
        settle_network=settle_network,
        settle_address=settle_address,
        settle_memo=settle_memo,
        affiliate_id=affiliate_id or client.affiliate_id or "",
        refund_address=refund_address,
        refund_memo=refund_memo,
        external_id=external_id,
    )

    headers = {}
    if user_ip or client.user_ip:
        headers[HEADER_USER_IP] = user_ip or client.user_ip or ""

    response = client.post(
        "/shifts/variable",
        json_data=request_data.model_dump(by_alias=True, exclude_none=True),
        headers=headers,
        require_auth=True,
        require_user_ip=bool(user_ip or client.user_ip),
    )
    return Shift(**response)


async def create_variable_shift_async(
    client: "AsyncSideShiftClient",
    deposit_coin: str,
    settle_coin: str,
    settle_address: str,
    deposit_network: str | None = None,
    settle_network: str | None = None,
    affiliate_id: str | None = None,
    settle_memo: str | None = None,
    refund_address: str | None = None,
    refund_memo: str | None = None,
    external_id: str | None = None,
    user_ip: str | None = None,
) -> Shift:
    """Create a variable rate shift (async).

    Args:
        client: Async SideShift client instance
        deposit_coin: Deposit coin ticker
        settle_coin: Settle coin ticker
        settle_address: Address to receive the settle coin
        deposit_network: Deposit network (required for non-native/multi-network tokens)
        settle_network: Settle network (required for non-native/multi-network tokens)
        affiliate_id: Affiliate ID (uses client default if not provided)
        settle_memo: Memo for coins that require it
        refund_address: Refund address (optional)
        refund_memo: Refund memo (optional)
        external_id: Integration's own ID (optional)
        user_ip: End-user IP address (uses client default if not provided)

    Returns:
        Shift object
    """
    # Input validation
    validate_non_empty_string(deposit_coin, "deposit_coin")
    validate_non_empty_string(settle_coin, "settle_coin")
    validate_non_empty_string(settle_address, "settle_address")

    request_data = VariableShiftRequest(
        deposit_coin=deposit_coin,
        deposit_network=deposit_network,
        settle_coin=settle_coin,
        settle_network=settle_network,
        settle_address=settle_address,
        settle_memo=settle_memo,
        affiliate_id=affiliate_id or client.affiliate_id or "",
        refund_address=refund_address,
        refund_memo=refund_memo,
        external_id=external_id,
    )

    headers = {}
    if user_ip or client.user_ip:
        headers[HEADER_USER_IP] = user_ip or client.user_ip or ""

    response = await client.post(
        "/shifts/variable",
        json_data=request_data.model_dump(by_alias=True, exclude_none=True),
        headers=headers,
        require_auth=True,
        require_user_ip=bool(user_ip or client.user_ip),
    )
    return Shift(**response)


def set_refund_address(
    client: "SideShiftClient",
    shift_id: str,
    address: str,
    memo: str | None = None,
) -> Shift:
    """Set or update refund address for a shift.

    Args:
        client: SideShift client instance
        shift_id: Unique shift identifier
        address: Refund address
        memo: Memo for addresses that require it (optional)

    Returns:
        Updated Shift object
    """
    # Input validation
    validate_non_empty_string(shift_id, "shift_id")
    validate_non_empty_string(address, "address")

    request_data = SetRefundAddressRequest(address=address, memo=memo)
    response = client.post(
        f"/shifts/{shift_id}/set-refund-address",
        json_data=request_data.model_dump(exclude_none=True),
        require_auth=True,
    )
    return Shift(**response)


async def set_refund_address_async(
    client: "AsyncSideShiftClient",
    shift_id: str,
    address: str,
    memo: str | None = None,
) -> Shift:
    """Set or update refund address for a shift (async).

    Args:
        client: Async SideShift client instance
        shift_id: Unique shift identifier
        address: Refund address
        memo: Memo for addresses that require it (optional)

    Returns:
        Updated Shift object
    """
    # Input validation
    validate_non_empty_string(shift_id, "shift_id")
    validate_non_empty_string(address, "address")

    request_data = SetRefundAddressRequest(address=address, memo=memo)
    response = await client.post(
        f"/shifts/{shift_id}/set-refund-address",
        json_data=request_data.model_dump(exclude_none=True),
        require_auth=True,
    )
    return Shift(**response)


def cancel_order(client: "SideShiftClient", order_id: str) -> None:
    """Cancel an order.

    Args:
        client: SideShift client instance
        order_id: Order ID to cancel
    """
    request_data = CancelOrderRequest(order_id=order_id)
    client.post(
        "/cancel-order",
        json_data=request_data.model_dump(by_alias=True),
        require_auth=True,
    )


async def cancel_order_async(client: "AsyncSideShiftClient", order_id: str) -> None:
    """Cancel an order (async).

    Args:
        client: Async SideShift client instance
        order_id: Order ID to cancel
    """
    request_data = CancelOrderRequest(order_id=order_id)
    await client.post(
        "/cancel-order",
        json_data=request_data.model_dump(by_alias=True),
        require_auth=True,
    )
