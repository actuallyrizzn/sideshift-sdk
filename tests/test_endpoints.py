"""Tests for endpoint functions."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from sideshift_sdk.client import AsyncSideShiftClient, SideShiftClient
from sideshift_sdk.endpoints import account, checkout, coins, pairs, quotes, shifts
from sideshift_sdk.exceptions import SideShiftAPIError


def test_get_coins():
    """Test get_coins endpoint."""
    client = SideShiftClient()

    mock_response = [
        {
            "networks": ["bitcoin"],
            "coin": "btc",
            "name": "Bitcoin",
            "hasMemo": False,
            "fixedOnly": False,
            "variableOnly": False,
            "networksWithMemo": [],
        }
    ]

    with patch.object(client, "get", return_value=mock_response):
        coins_list = coins.get_coins(client)
        assert len(coins_list) == 1
        assert coins_list[0].coin == "btc"


def test_get_pair():
    """Test get_pair endpoint."""
    client = SideShiftClient(secret="test-secret", affiliate_id="test-affiliate")

    mock_response = {
        "min": "0.001",
        "max": "10.0",
        "rate": "15.5",
        "depositCoin": "btc",
        "settleCoin": "eth",
        "depositNetwork": "bitcoin",
        "settleNetwork": "mainnet",
    }

    with patch.object(client, "get", return_value=mock_response):
        pair = pairs.get_pair(client, from_coin="btc", to_coin="eth")
        assert pair.min == "0.001"
        assert pair.max == "10.0"
        assert pair.rate == "15.5"


def test_request_quote():
    """Test request_quote endpoint."""
    client = SideShiftClient(secret="test-secret", affiliate_id="test-affiliate")

    mock_response = {
        "id": "test-quote-id",
        "createdAt": "2024-01-01T00:00:00Z",
        "depositCoin": "btc",
        "settleCoin": "eth",
        "depositNetwork": "bitcoin",
        "settleNetwork": "mainnet",
        "expiresAt": "2024-01-01T00:15:00Z",
        "depositAmount": "0.1",
        "settleAmount": "1.5",
        "rate": "15.0",
    }

    with patch.object(client, "post", return_value=mock_response):
        quote = quotes.request_quote(
            client,
            deposit_coin="btc",
            settle_coin="eth",
            deposit_amount="0.1",
        )
        assert quote.id == "test-quote-id"
        assert quote.rate == "15.0"


def test_request_quote_missing_amounts():
    """Test request_quote with missing amounts raises ValueError."""
    client = SideShiftClient(secret="test-secret", affiliate_id="test-affiliate")

    with pytest.raises(ValueError, match="Either deposit_amount or settle_amount must be provided"):
        quotes.request_quote(
            client,
            deposit_coin="btc",
            settle_coin="eth",
        )


def test_create_fixed_shift():
    """Test create_fixed_shift endpoint."""
    client = SideShiftClient(secret="test-secret", affiliate_id="test-affiliate")

    mock_response = {
        "id": "test-shift-id",
        "createdAt": "2024-01-01T00:00:00Z",
        "depositCoin": "btc",
        "settleCoin": "eth",
        "depositNetwork": "bitcoin",
        "settleNetwork": "mainnet",
        "depositAddress": "bc1q...",
        "settleAddress": "0x...",
        "depositMin": "0.001",
        "depositMax": "10.0",
        "type": "fixed",
        "quoteId": "test-quote-id",
        "depositAmount": "0.1",
        "settleAmount": "1.5",
        "expiresAt": "2024-01-01T00:15:00Z",
        "status": "waiting",
        "rate": "15.0",
    }

    with patch.object(client, "post", return_value=mock_response):
        shift = shifts.create_fixed_shift(
            client,
            quote_id="test-quote-id",
            settle_address="0x...",
        )
        assert shift.id == "test-shift-id"
        assert shift.type == "fixed"


def test_create_variable_shift():
    """Test create_variable_shift endpoint."""
    client = SideShiftClient(secret="test-secret", affiliate_id="test-affiliate")

    mock_response = {
        "id": "test-shift-id",
        "createdAt": "2024-01-01T00:00:00Z",
        "depositCoin": "btc",
        "settleCoin": "eth",
        "depositNetwork": "bitcoin",
        "settleNetwork": "mainnet",
        "depositAddress": "bc1q...",
        "settleAddress": "0x...",
        "depositMin": "0.001",
        "depositMax": "10.0",
        "type": "variable",
        "status": "waiting",
    }

    with patch.object(client, "post", return_value=mock_response):
        shift = shifts.create_variable_shift(
            client,
            deposit_coin="btc",
            settle_coin="eth",
            settle_address="0x...",
        )
        assert shift.id == "test-shift-id"
        assert shift.type == "variable"


def test_get_shift():
    """Test get_shift endpoint."""
    client = SideShiftClient()

    mock_response = {
        "id": "test-shift-id",
        "createdAt": "2024-01-01T00:00:00Z",
        "depositCoin": "btc",
        "settleCoin": "eth",
        "depositNetwork": "bitcoin",
        "settleNetwork": "mainnet",
        "settleAddress": "0x...",
        "type": "fixed",
        "status": "complete",
    }

    with patch.object(client, "get", return_value=mock_response):
        shift = shifts.get_shift(client, shift_id="test-shift-id")
        assert shift.id == "test-shift-id"
        assert shift.status == "complete"


def test_get_bulk_shifts():
    """Test get_bulk_shifts endpoint."""
    client = SideShiftClient()

    mock_response = [
        {
            "id": "shift-1",
            "createdAt": "2024-01-01T00:00:00Z",
            "depositCoin": "btc",
            "settleCoin": "eth",
            "depositNetwork": "bitcoin",
            "settleNetwork": "mainnet",
            "settleAddress": "0x...",
            "type": "fixed",
            "status": "complete",
        },
        {
            "id": "shift-2",
            "createdAt": "2024-01-01T00:00:00Z",
            "depositCoin": "eth",
            "settleCoin": "btc",
            "depositNetwork": "mainnet",
            "settleNetwork": "bitcoin",
            "settleAddress": "bc1q...",
            "type": "variable",
            "status": "waiting",
        },
    ]

    with patch.object(client, "get", return_value=mock_response):
        shifts_list = shifts.get_bulk_shifts(client, shift_ids=["shift-1", "shift-2"])
        assert len(shifts_list) == 2
        assert shifts_list[0].id == "shift-1"
        assert shifts_list[1].id == "shift-2"


def test_get_recent_shifts():
    """Test get_recent_shifts endpoint."""
    client = SideShiftClient()

    mock_response = [
        {
            "createdAt": "2024-01-01T00:00:00Z",
            "depositCoin": "btc",
            "depositNetwork": "bitcoin",
            "depositAmount": "0.1",
            "settleCoin": "eth",
            "settleNetwork": "mainnet",
            "settleAmount": "1.5",
        }
    ]

    with patch.object(client, "get", return_value=mock_response):
        recent = shifts.get_recent_shifts(client, limit=10)
        assert len(recent) == 1
        assert recent[0].deposit_coin == "btc"


def test_get_recent_shifts_invalid_limit():
    """Test get_recent_shifts with invalid limit."""
    client = SideShiftClient()

    with pytest.raises(ValueError, match="limit must be between 1 and 100"):
        shifts.get_recent_shifts(client, limit=0)

    with pytest.raises(ValueError, match="limit must be between 1 and 100"):
        shifts.get_recent_shifts(client, limit=101)


def test_get_account():
    """Test get_account endpoint."""
    client = SideShiftClient(secret="test-secret")

    mock_response = {
        "id": "test-account-id",
        "lifetimeStakingRewards": "100.0",
        "unstaking": "10.0",
        "staked": "50.0",
        "available": "40.0",
        "totalBalance": "100.0",
    }

    with patch.object(client, "get", return_value=mock_response):
        account_info = account.get_account(client)
        assert account_info.id == "test-account-id"
        assert account_info.total_balance == "100.0"


def test_get_permissions():
    """Test get_permissions endpoint."""
    client = SideShiftClient(user_ip="1.2.3.4")

    mock_response = {"createShift": True}

    with patch.object(client, "get", return_value=mock_response):
        permissions = account.get_permissions(client)
        assert permissions.create_shift is True


def test_get_xai_stats():
    """Test get_xai_stats endpoint."""
    client = SideShiftClient()

    mock_response = {
        "totalSupply": 1000000,
        "circulatingSupply": 500000,
        "numberOfStakers": 1000,
        "latestAnnualPercentageYield": "5.0",
        "latestDistributedXai": "1000.0",
        "totalStaked": "500000.0",
        "averageAnnualPercentageYield": "4.5",
        "totalValueLocked": "1000000.0",
        "totalValueLockedRatio": "0.5",
        "xaiPriceUsd": "1.0",
        "svxaiPriceUsd": "1.05",
        "svxaiPriceXai": "1.05",
    }

    with patch.object(client, "get", return_value=mock_response):
        stats = account.get_xai_stats(client)
        assert stats.total_supply == 1000000
        assert stats.xai_price_usd == "1.0"


def test_get_coin_icon():
    """Test get_coin_icon endpoint."""
    client = SideShiftClient()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"<svg>...</svg>"

    with patch.object(client._session, "get", return_value=mock_response):
        icon = coins.get_coin_icon(client, "btc", format="svg")
        assert icon == b"<svg>...</svg>"


def test_get_coin_icon_png():
    """Test get_coin_icon with PNG format."""
    client = SideShiftClient()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"\x89PNG..."

    with patch.object(client._session, "get", return_value=mock_response):
        icon = coins.get_coin_icon(client, "btc", format="png")
        assert icon == b"\x89PNG..."


def test_get_coin_icon_error():
    """Test get_coin_icon with error response."""
    client = SideShiftClient()
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"message": "Bad request"}

    with patch.object(client._session, "get", return_value=mock_response):
        with pytest.raises(SideShiftAPIError):
            coins.get_coin_icon(client, "invalid-coin")


def test_get_pairs():
    """Test get_pairs endpoint."""
    client = SideShiftClient(secret="test-secret", affiliate_id="test-affiliate")

    mock_response = [
        {
            "depositCoin": "btc",
            "settleCoin": "eth",
            "depositNetwork": "bitcoin",
            "settleNetwork": "mainnet",
            "min": "0.001",
            "max": "10.0",
            "rate": "15.5",
        },
        {
            "depositCoin": "eth",
            "settleCoin": "btc",
            "depositNetwork": "mainnet",
            "settleNetwork": "bitcoin",
            "min": "0.01",
            "max": "100.0",
            "rate": "0.064",
        },
    ]

    with patch.object(client, "get", return_value=mock_response):
        pairs_list = pairs.get_pairs(client, pairs=["btc", "eth"])
        assert len(pairs_list) == 2
        assert pairs_list[0].deposit_coin == "btc"
        assert pairs_list[1].deposit_coin == "eth"


def test_get_pair_with_amount():
    """Test get_pair with amount parameter."""
    client = SideShiftClient(secret="test-secret", affiliate_id="test-affiliate")

    mock_response = {
        "min": "0.001",
        "max": "10.0",
        "rate": "15.5",
        "depositCoin": "btc",
        "settleCoin": "eth",
        "depositNetwork": "bitcoin",
        "settleNetwork": "mainnet",
    }

    with patch.object(client, "get", return_value=mock_response):
        pair = pairs.get_pair(client, from_coin="btc", to_coin="eth", amount=1000.0)
        assert pair.rate == "15.5"


def test_get_pair_with_commission_rate():
    """Test get_pair with commission_rate parameter."""
    client = SideShiftClient(secret="test-secret", affiliate_id="test-affiliate")

    mock_response = {
        "min": "0.001",
        "max": "10.0",
        "rate": "15.5",
        "depositCoin": "btc",
        "settleCoin": "eth",
        "depositNetwork": "bitcoin",
        "settleNetwork": "mainnet",
    }

    with patch.object(client, "get", return_value=mock_response):
        pair = pairs.get_pair(client, from_coin="btc", to_coin="eth", commission_rate="1.0")
        assert pair.rate == "15.5"


def test_request_quote_with_settle_amount():
    """Test request_quote with settle_amount instead of deposit_amount."""
    client = SideShiftClient(secret="test-secret", affiliate_id="test-affiliate")

    mock_response = {
        "id": "test-quote-id",
        "createdAt": "2024-01-01T00:00:00Z",
        "depositCoin": "btc",
        "settleCoin": "eth",
        "depositNetwork": "bitcoin",
        "settleNetwork": "mainnet",
        "expiresAt": "2024-01-01T00:15:00Z",
        "depositAmount": "0.1",
        "settleAmount": "1.5",
        "rate": "15.0",
    }

    with patch.object(client, "post", return_value=mock_response):
        quote = quotes.request_quote(
            client,
            deposit_coin="btc",
            settle_coin="eth",
            settle_amount="1.5",
        )
        assert quote.id == "test-quote-id"


def test_request_quote_with_user_ip():
    """Test request_quote with user_ip parameter."""
    client = SideShiftClient(secret="test-secret", affiliate_id="test-affiliate")

    mock_response = {
        "id": "test-quote-id",
        "createdAt": "2024-01-01T00:00:00Z",
        "depositCoin": "btc",
        "settleCoin": "eth",
        "depositNetwork": "bitcoin",
        "settleNetwork": "mainnet",
        "expiresAt": "2024-01-01T00:15:00Z",
        "depositAmount": "0.1",
        "settleAmount": "1.5",
        "rate": "15.0",
    }

    with patch.object(client, "post", return_value=mock_response):
        quote = quotes.request_quote(
            client,
            deposit_coin="btc",
            settle_coin="eth",
            deposit_amount="0.1",
            user_ip="1.2.3.4",
        )
        assert quote.id == "test-quote-id"


def test_set_refund_address():
    """Test set_refund_address endpoint."""
    client = SideShiftClient(secret="test-secret")

    mock_response = {
        "id": "test-shift-id",
        "createdAt": "2024-01-01T00:00:00Z",
        "depositCoin": "btc",
        "settleCoin": "eth",
        "depositNetwork": "bitcoin",
        "settleNetwork": "mainnet",
        "settleAddress": "0x...",
        "refundAddress": "bc1q...",
        "type": "fixed",
        "status": "waiting",
    }

    with patch.object(client, "post", return_value=mock_response):
        shift = shifts.set_refund_address(client, shift_id="test-shift-id", address="bc1q...")
        assert shift.refund_address == "bc1q..."


def test_set_refund_address_with_memo():
    """Test set_refund_address with memo."""
    client = SideShiftClient(secret="test-secret")

    mock_response = {
        "id": "test-shift-id",
        "createdAt": "2024-01-01T00:00:00Z",
        "depositCoin": "btc",
        "settleCoin": "eth",
        "depositNetwork": "bitcoin",
        "settleNetwork": "mainnet",
        "settleAddress": "0x...",
        "refundAddress": "bc1q...",
        "refundMemo": "12345",
        "type": "fixed",
        "status": "waiting",
    }

    with patch.object(client, "post", return_value=mock_response):
        shift = shifts.set_refund_address(
            client, shift_id="test-shift-id", address="bc1q...", memo="12345"
        )
        assert shift.refund_memo == "12345"


def test_cancel_order():
    """Test cancel_order endpoint."""
    client = SideShiftClient(secret="test-secret")

    mock_response = {}  # 204 No Content

    with patch.object(client, "post", return_value=mock_response):
        shifts.cancel_order(client, order_id="test-order-id")
        # Should not raise


def test_get_checkout():
    """Test get_checkout endpoint."""
    client = SideShiftClient()

    mock_response = {
        "id": "test-checkout-id",
        "settleCoin": "eth",
        "settleNetwork": "mainnet",
        "settleAddress": "0x...",
        "settleAmount": "1.0",
        "updatedAt": "2024-01-01T00:00:00Z",
        "createdAt": "2024-01-01T00:00:00Z",
        "affiliateId": "test-affiliate",
        "successUrl": "https://example.com/success",
        "cancelUrl": "https://example.com/cancel",
    }

    with patch.object(client, "get", return_value=mock_response):
        checkout_obj = checkout.get_checkout(client, checkout_id="test-checkout-id")
        assert checkout_obj.id == "test-checkout-id"
        assert checkout_obj.settle_coin == "eth"


def test_create_checkout():
    """Test create_checkout endpoint."""
    client = SideShiftClient(secret="test-secret", affiliate_id="test-affiliate", user_ip="1.2.3.4")

    mock_response = {
        "id": "test-checkout-id",
        "settleCoin": "eth",
        "settleNetwork": "mainnet",
        "settleAddress": "0x...",
        "settleAmount": "1.0",
        "updatedAt": "2024-01-01T00:00:00Z",
        "createdAt": "2024-01-01T00:00:00Z",
        "affiliateId": "test-affiliate",
        "successUrl": "https://example.com/success",
        "cancelUrl": "https://example.com/cancel",
    }

    with patch.object(client, "post", return_value=mock_response):
        checkout_obj = checkout.create_checkout(
            client,
            settle_coin="eth",
            settle_network="mainnet",
            settle_amount="1.0",
            settle_address="0x...",
            affiliate_id="test-affiliate",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )
        assert checkout_obj.id == "test-checkout-id"


def test_create_checkout_missing_user_ip():
    """Test create_checkout without user_ip raises error."""
    client = SideShiftClient(secret="test-secret", affiliate_id="test-affiliate")

    with pytest.raises(ValueError, match="user_ip is required"):
        checkout.create_checkout(
            client,
            settle_coin="eth",
            settle_network="mainnet",
            settle_amount="1.0",
            settle_address="0x...",
            affiliate_id="test-affiliate",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )


def test_create_checkout_with_memo():
    """Test create_checkout with settle_memo."""
    client = SideShiftClient(secret="test-secret", affiliate_id="test-affiliate", user_ip="1.2.3.4")

    mock_response = {
        "id": "test-checkout-id",
        "settleCoin": "eth",
        "settleNetwork": "mainnet",
        "settleAddress": "0x...",
        "settleMemo": "12345",
        "settleAmount": "1.0",
        "updatedAt": "2024-01-01T00:00:00Z",
        "createdAt": "2024-01-01T00:00:00Z",
        "affiliateId": "test-affiliate",
        "successUrl": "https://example.com/success",
        "cancelUrl": "https://example.com/cancel",
    }

    with patch.object(client, "post", return_value=mock_response):
        checkout_obj = checkout.create_checkout(
            client,
            settle_coin="eth",
            settle_network="mainnet",
            settle_amount="1.0",
            settle_address="0x...",
            affiliate_id="test-affiliate",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            settle_memo="12345",
        )
        assert checkout_obj.settle_memo == "12345"


# Async tests
@pytest.mark.asyncio
async def test_get_coins_async():
    """Test get_coins_async endpoint."""
    async with AsyncSideShiftClient() as client:
        mock_response = [
            {
                "networks": ["bitcoin"],
                "coin": "btc",
                "name": "Bitcoin",
                "hasMemo": False,
                "fixedOnly": False,
                "variableOnly": False,
                "networksWithMemo": [],
            }
        ]

        with patch.object(client, "get", return_value=mock_response):
            coins_list = await coins.get_coins_async(client)
            assert len(coins_list) == 1
            assert coins_list[0].coin == "btc"


@pytest.mark.asyncio
async def test_get_coin_icon_async():
    """Test get_coin_icon_async endpoint."""
    async with AsyncSideShiftClient() as client:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<svg>...</svg>"
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch.object(client, "_get_client", return_value=mock_client):
            icon = await coins.get_coin_icon_async(client, "btc", format="svg")
            assert icon == b"<svg>...</svg>"


@pytest.mark.asyncio
async def test_get_pair_async():
    """Test get_pair_async endpoint."""
    async with AsyncSideShiftClient(secret="test-secret", affiliate_id="test-affiliate") as client:
        mock_response = {
            "min": "0.001",
            "max": "10.0",
            "rate": "15.5",
            "depositCoin": "btc",
            "settleCoin": "eth",
            "depositNetwork": "bitcoin",
            "settleNetwork": "mainnet",
        }

        with patch.object(client, "get", return_value=mock_response):
            pair = await pairs.get_pair_async(client, from_coin="btc", to_coin="eth")
            assert pair.rate == "15.5"


@pytest.mark.asyncio
async def test_get_pairs_async():
    """Test get_pairs_async endpoint."""
    async with AsyncSideShiftClient(secret="test-secret", affiliate_id="test-affiliate") as client:
        mock_response = [
            {
                "depositCoin": "btc",
                "settleCoin": "eth",
                "depositNetwork": "bitcoin",
                "settleNetwork": "mainnet",
                "min": "0.001",
                "max": "10.0",
                "rate": "15.5",
            }
        ]

        with patch.object(client, "get", return_value=mock_response):
            pairs_list = await pairs.get_pairs_async(client, pairs=["btc", "eth"])
            assert len(pairs_list) == 1


@pytest.mark.asyncio
async def test_request_quote_async():
    """Test request_quote_async endpoint."""
    async with AsyncSideShiftClient(secret="test-secret", affiliate_id="test-affiliate") as client:
        mock_response = {
            "id": "test-quote-id",
            "createdAt": "2024-01-01T00:00:00Z",
            "depositCoin": "btc",
            "settleCoin": "eth",
            "depositNetwork": "bitcoin",
            "settleNetwork": "mainnet",
            "expiresAt": "2024-01-01T00:15:00Z",
            "depositAmount": "0.1",
            "settleAmount": "1.5",
            "rate": "15.0",
        }

        with patch.object(client, "post", return_value=mock_response):
            quote = await quotes.request_quote_async(
                client,
                deposit_coin="btc",
                settle_coin="eth",
                deposit_amount="0.1",
            )
            assert quote.id == "test-quote-id"


@pytest.mark.asyncio
async def test_get_shift_async():
    """Test get_shift_async endpoint."""
    async with AsyncSideShiftClient() as client:
        mock_response = {
            "id": "test-shift-id",
            "createdAt": "2024-01-01T00:00:00Z",
            "depositCoin": "btc",
            "settleCoin": "eth",
            "depositNetwork": "bitcoin",
            "settleNetwork": "mainnet",
            "settleAddress": "0x...",
            "type": "fixed",
            "status": "complete",
        }

        with patch.object(client, "get", return_value=mock_response):
            shift = await shifts.get_shift_async(client, shift_id="test-shift-id")
            assert shift.id == "test-shift-id"


@pytest.mark.asyncio
async def test_get_bulk_shifts_async():
    """Test get_bulk_shifts_async endpoint."""
    async with AsyncSideShiftClient() as client:
        mock_response = [
            {
                "id": "shift-1",
                "createdAt": "2024-01-01T00:00:00Z",
                "depositCoin": "btc",
                "settleCoin": "eth",
                "depositNetwork": "bitcoin",
                "settleNetwork": "mainnet",
                "settleAddress": "0x...",
                "type": "fixed",
                "status": "complete",
            }
        ]

        with patch.object(client, "get", return_value=mock_response):
            shifts_list = await shifts.get_bulk_shifts_async(client, shift_ids=["shift-1"])
            assert len(shifts_list) == 1


@pytest.mark.asyncio
async def test_get_recent_shifts_async():
    """Test get_recent_shifts_async endpoint."""
    async with AsyncSideShiftClient() as client:
        mock_response = [
            {
                "createdAt": "2024-01-01T00:00:00Z",
                "depositCoin": "btc",
                "depositNetwork": "bitcoin",
                "depositAmount": "0.1",
                "settleCoin": "eth",
                "settleNetwork": "mainnet",
                "settleAmount": "1.5",
            }
        ]

        with patch.object(client, "get", return_value=mock_response):
            recent = await shifts.get_recent_shifts_async(client, limit=10)
            assert len(recent) == 1


@pytest.mark.asyncio
async def test_create_fixed_shift_async():
    """Test create_fixed_shift_async endpoint."""
    async with AsyncSideShiftClient(secret="test-secret", affiliate_id="test-affiliate") as client:
        mock_response = {
            "id": "test-shift-id",
            "createdAt": "2024-01-01T00:00:00Z",
            "depositCoin": "btc",
            "settleCoin": "eth",
            "depositNetwork": "bitcoin",
            "settleNetwork": "mainnet",
            "depositAddress": "bc1q...",
            "settleAddress": "0x...",
            "type": "fixed",
            "status": "waiting",
        }

        with patch.object(client, "post", return_value=mock_response):
            shift = await shifts.create_fixed_shift_async(
                client,
                quote_id="test-quote-id",
                settle_address="0x...",
            )
            assert shift.id == "test-shift-id"


@pytest.mark.asyncio
async def test_create_variable_shift_async():
    """Test create_variable_shift_async endpoint."""
    async with AsyncSideShiftClient(secret="test-secret", affiliate_id="test-affiliate") as client:
        mock_response = {
            "id": "test-shift-id",
            "createdAt": "2024-01-01T00:00:00Z",
            "depositCoin": "btc",
            "settleCoin": "eth",
            "depositNetwork": "bitcoin",
            "settleNetwork": "mainnet",
            "depositAddress": "bc1q...",
            "settleAddress": "0x...",
            "type": "variable",
            "status": "waiting",
        }

        with patch.object(client, "post", return_value=mock_response):
            shift = await shifts.create_variable_shift_async(
                client,
                deposit_coin="btc",
                settle_coin="eth",
                settle_address="0x...",
            )
            assert shift.type == "variable"


@pytest.mark.asyncio
async def test_set_refund_address_async():
    """Test set_refund_address_async endpoint."""
    async with AsyncSideShiftClient(secret="test-secret") as client:
        mock_response = {
            "id": "test-shift-id",
            "createdAt": "2024-01-01T00:00:00Z",
            "depositCoin": "btc",
            "settleCoin": "eth",
            "depositNetwork": "bitcoin",
            "settleNetwork": "mainnet",
            "settleAddress": "0x...",
            "refundAddress": "bc1q...",
            "type": "fixed",
            "status": "waiting",
        }

        with patch.object(client, "post", return_value=mock_response):
            shift = await shifts.set_refund_address_async(
                client, shift_id="test-shift-id", address="bc1q..."
            )
            assert shift.refund_address == "bc1q..."


@pytest.mark.asyncio
async def test_cancel_order_async():
    """Test cancel_order_async endpoint."""
    async with AsyncSideShiftClient(secret="test-secret") as client:
        mock_response = {}

        with patch.object(client, "post", return_value=mock_response):
            await shifts.cancel_order_async(client, order_id="test-order-id")
            # Should not raise


@pytest.mark.asyncio
async def test_get_account_async():
    """Test get_account_async endpoint."""
    async with AsyncSideShiftClient(secret="test-secret") as client:
        mock_response = {
            "id": "test-account-id",
            "lifetimeStakingRewards": "100.0",
            "unstaking": "10.0",
            "staked": "50.0",
            "available": "40.0",
            "totalBalance": "100.0",
        }

        with patch.object(client, "get", return_value=mock_response):
            account_info = await account.get_account_async(client)
            assert account_info.id == "test-account-id"


@pytest.mark.asyncio
async def test_get_permissions_async():
    """Test get_permissions_async endpoint."""
    async with AsyncSideShiftClient(user_ip="1.2.3.4") as client:
        mock_response = {"createShift": True}

        with patch.object(client, "get", return_value=mock_response):
            permissions = await account.get_permissions_async(client)
            assert permissions.create_shift is True


@pytest.mark.asyncio
async def test_get_xai_stats_async():
    """Test get_xai_stats_async endpoint."""
    async with AsyncSideShiftClient() as client:
        mock_response = {
            "totalSupply": 1000000,
            "circulatingSupply": 500000,
            "numberOfStakers": 1000,
            "latestAnnualPercentageYield": "5.0",
            "latestDistributedXai": "1000.0",
            "totalStaked": "500000.0",
            "averageAnnualPercentageYield": "4.5",
            "totalValueLocked": "1000000.0",
            "totalValueLockedRatio": "0.5",
            "xaiPriceUsd": "1.0",
            "svxaiPriceUsd": "1.05",
            "svxaiPriceXai": "1.05",
        }

        with patch.object(client, "get", return_value=mock_response):
            stats = await account.get_xai_stats_async(client)
            assert stats.total_supply == 1000000


@pytest.mark.asyncio
async def test_get_checkout_async():
    """Test get_checkout_async endpoint."""
    async with AsyncSideShiftClient() as client:
        mock_response = {
            "id": "test-checkout-id",
            "settleCoin": "eth",
            "settleNetwork": "mainnet",
            "settleAddress": "0x...",
            "settleAmount": "1.0",
            "updatedAt": "2024-01-01T00:00:00Z",
            "createdAt": "2024-01-01T00:00:00Z",
            "affiliateId": "test-affiliate",
            "successUrl": "https://example.com/success",
            "cancelUrl": "https://example.com/cancel",
        }

        with patch.object(client, "get", return_value=mock_response):
            checkout_obj = await checkout.get_checkout_async(client, checkout_id="test-checkout-id")
            assert checkout_obj.id == "test-checkout-id"


@pytest.mark.asyncio
async def test_create_checkout_async():
    """Test create_checkout_async endpoint."""
    async with AsyncSideShiftClient(
        secret="test-secret", affiliate_id="test-affiliate", user_ip="1.2.3.4"
    ) as client:
        mock_response = {
            "id": "test-checkout-id",
            "settleCoin": "eth",
            "settleNetwork": "mainnet",
            "settleAddress": "0x...",
            "settleAmount": "1.0",
            "updatedAt": "2024-01-01T00:00:00Z",
            "createdAt": "2024-01-01T00:00:00Z",
            "affiliateId": "test-affiliate",
            "successUrl": "https://example.com/success",
            "cancelUrl": "https://example.com/cancel",
        }

        with patch.object(client, "post", return_value=mock_response):
            checkout_obj = await checkout.create_checkout_async(
                client,
                settle_coin="eth",
                settle_network="mainnet",
                settle_amount="1.0",
                settle_address="0x...",
                affiliate_id="test-affiliate",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )
            assert checkout_obj.id == "test-checkout-id"
