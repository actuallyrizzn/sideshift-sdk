"""Pairs endpoints."""

from typing import TYPE_CHECKING

from sideshift_sdk.models import PairInfo
from sideshift_sdk.utils import validate_non_empty_string

if TYPE_CHECKING:
    from sideshift_sdk.client import AsyncSideShiftClient, SideShiftClient


def get_pair(
    client: "SideShiftClient",
    from_coin: str,
    to_coin: str,
    affiliate_id: str | None = None,
    amount: float | None = None,
    commission_rate: str | None = None,
) -> PairInfo:
    """Get pair information (min, max, rate).

    Args:
        client: SideShift client instance
        from_coin: Source coin-network identifier
        to_coin: Destination coin-network identifier
        affiliate_id: Affiliate ID (uses client default if not provided)
        amount: Deposit value in USD (defaults to 500)
        commission_rate: Commission rate

    Returns:
        PairInfo object

    Examples:
        >>> client = SideShiftClient(secret="your-secret", affiliate_id="your-id")
        >>> pair = get_pair(client, from_coin="btc", to_coin="eth")
        >>> print(f"Rate: {pair.rate}, Min: {pair.min}, Max: {pair.max}")
    """
    params: dict[str, str | float] = {
        "affiliateId": affiliate_id or client.affiliate_id or "",
    }

    if amount is not None:
        params["amount"] = amount

    if commission_rate:
        params["commissionRate"] = commission_rate

    response = client.get(f"/pair/{from_coin}/{to_coin}", params=params, require_auth=True)
    return PairInfo(**response)


async def get_pair_async(
    client: "AsyncSideShiftClient",
    from_coin: str,
    to_coin: str,
    affiliate_id: str | None = None,
    amount: float | None = None,
    commission_rate: str | None = None,
) -> PairInfo:
    """Get pair information (min, max, rate) (async).

    Args:
        client: Async SideShift client instance
        from_coin: Source coin-network identifier
        to_coin: Destination coin-network identifier
        affiliate_id: Affiliate ID (uses client default if not provided)
        amount: Deposit value in USD (defaults to 500)
        commission_rate: Commission rate

    Returns:
        PairInfo object
    """
    # Input validation
    validate_non_empty_string(from_coin, "from_coin")
    validate_non_empty_string(to_coin, "to_coin")
    
    params: dict[str, str | float] = {
        "affiliateId": affiliate_id or client.affiliate_id or "",
    }

    if amount is not None:
        params["amount"] = amount

    if commission_rate:
        params["commissionRate"] = commission_rate

    response = await client.get(f"/pair/{from_coin}/{to_coin}", params=params, require_auth=True)
    return PairInfo(**response)


def get_pairs(
    client: "SideShiftClient",
    pairs: list[str],
    affiliate_id: str | None = None,
    commission_rate: str | None = None,
) -> list[PairInfo]:
    """Get pair information for multiple pairs.

    Args:
        client: SideShift client instance
        pairs: List of coin-network identifiers (e.g., ['btc-mainnet', 'usdc-bsc', 'bch', 'eth'])
        affiliate_id: Affiliate ID (uses client default if not provided)
        commission_rate: Commission rate

    Returns:
        List of PairInfo objects

    Examples:
        >>> client = SideShiftClient(secret="your-secret", affiliate_id="your-id")
        >>> pairs_list = get_pairs(client, pairs=["btc-mainnet", "eth-mainnet"])
        >>> for pair in pairs_list:
        ...     print(f"{pair.from_coin} -> {pair.to_coin}: {pair.rate}")
    """
    params: dict[str, str] = {
        "pairs": ",".join(pairs),
        "affiliateId": affiliate_id or client.affiliate_id or "",
    }

    if commission_rate:
        params["commissionRate"] = commission_rate

    response = client.get("/pairs", params=params, require_auth=True)
    return [PairInfo(**pair_data) for pair_data in response]


async def get_pairs_async(
    client: "AsyncSideShiftClient",
    pairs: list[str],
    affiliate_id: str | None = None,
    commission_rate: str | None = None,
) -> list[PairInfo]:
    """Get pair information for multiple pairs (async).

    Args:
        client: Async SideShift client instance
        pairs: List of coin-network identifiers
        affiliate_id: Affiliate ID (uses client default if not provided)
        commission_rate: Commission rate

    Returns:
        List of PairInfo objects
    """
    params: dict[str, str] = {
        "pairs": ",".join(pairs),
        "affiliateId": affiliate_id or client.affiliate_id or "",
    }

    if commission_rate:
        params["commissionRate"] = commission_rate

    response = await client.get("/pairs", params=params, require_auth=True)
    return [PairInfo(**pair_data) for pair_data in response]
