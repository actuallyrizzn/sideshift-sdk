"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from sideshift_sdk.models import (
    Account,
    CancelOrderRequest,
    Checkout,
    CheckoutRequest,
    Coin,
    FixedShiftRequest,
    PairInfo,
    Permissions,
    Quote,
    QuoteRequest,
    RecentShift,
    SetRefundAddressRequest,
    Shift,
    VariableShiftRequest,
    XAIStats,
)


def test_coin_model():
    """Test Coin model validation."""
    coin_data = {
        "networks": ["bitcoin", "mainnet"],
        "coin": "btc",
        "name": "Bitcoin",
        "hasMemo": False,
        "fixedOnly": False,
        "variableOnly": False,
        "networksWithMemo": [],
        "depositOffline": False,
        "settleOffline": False,
    }

    coin = Coin(**coin_data)
    assert coin.coin == "btc"
    assert coin.name == "Bitcoin"
    assert len(coin.networks) == 2


def test_pair_info_model():
    """Test PairInfo model validation."""
    pair_data = {
        "min": "0.001",
        "max": "10.0",
        "rate": "15.5",
        "depositCoin": "btc",
        "settleCoin": "eth",
        "depositNetwork": "bitcoin",
        "settleNetwork": "mainnet",
    }

    pair = PairInfo(**pair_data)
    assert pair.min == "0.001"
    assert pair.max == "10.0"
    assert pair.rate == "15.5"
    assert pair.deposit_coin == "btc"
    assert pair.settle_coin == "eth"


def test_quote_model():
    """Test Quote model validation."""
    quote_data = {
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
        "affiliateId": "test-affiliate",
    }

    quote = Quote(**quote_data)
    assert quote.id == "test-quote-id"
    assert quote.deposit_amount == "0.1"
    assert quote.settle_amount == "1.5"
    assert quote.rate == "15.0"


def test_quote_request_model():
    """Test QuoteRequest model validation."""
    request = QuoteRequest(
        deposit_coin="btc",
        settle_coin="eth",
        deposit_amount="0.1",
        affiliate_id="test-affiliate",
    )

    assert request.deposit_coin == "btc"
    assert request.settle_coin == "eth"
    assert request.deposit_amount == "0.1"

    # Test that either deposit_amount or settle_amount is required
    with pytest.raises(ValidationError):
        QuoteRequest(
            deposit_coin="btc",
            settle_coin="eth",
            affiliate_id="test-affiliate",
        )


def test_shift_model():
    """Test Shift model validation."""
    shift_data = {
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
        "depositAmount": "0.1",
        "settleAmount": "1.5",
        "expiresAt": "2024-01-01T00:15:00Z",
        "status": "waiting",
        "rate": "15.0",
    }

    shift = Shift(**shift_data)
    assert shift.id == "test-shift-id"
    assert shift.type == "fixed"
    assert shift.status == "waiting"


def test_account_model():
    """Test Account model validation."""
    account_data = {
        "id": "test-account-id",
        "lifetimeStakingRewards": "100.0",
        "unstaking": "10.0",
        "staked": "50.0",
        "available": "40.0",
        "totalBalance": "100.0",
    }

    account = Account(**account_data)
    assert account.id == "test-account-id"
    assert account.available == "40.0"
    assert account.total_balance == "100.0"


def test_permissions_model():
    """Test Permissions model validation."""
    permissions_data = {"createShift": True}

    permissions = Permissions(**permissions_data)
    assert permissions.create_shift is True


def test_xai_stats_model():
    """Test XAIStats model validation."""
    xai_data = {
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

    xai_stats = XAIStats(**xai_data)
    assert xai_stats.total_supply == 1000000
    assert xai_stats.xai_price_usd == "1.0"


def test_checkout_model():
    """Test Checkout model validation."""
    checkout_data = {
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

    checkout = Checkout(**checkout_data)
    assert checkout.id == "test-checkout-id"
    assert checkout.settle_coin == "eth"
    assert checkout.settle_amount == "1.0"


def test_fixed_shift_request_model():
    """Test FixedShiftRequest model validation."""
    request = FixedShiftRequest(
        settle_address="0x...",
        affiliate_id="test-affiliate",
        quote_id="test-quote-id",
    )

    assert request.settle_address == "0x..."
    assert request.quote_id == "test-quote-id"


def test_variable_shift_request_model():
    """Test VariableShiftRequest model validation."""
    request = VariableShiftRequest(
        deposit_coin="btc",
        settle_coin="eth",
        settle_address="0x...",
        affiliate_id="test-affiliate",
    )

    assert request.deposit_coin == "btc"
    assert request.settle_coin == "eth"
    assert request.settle_address == "0x..."


def test_set_refund_address_request_model():
    """Test SetRefundAddressRequest model validation."""
    request = SetRefundAddressRequest(address="0x...")
    assert request.address == "0x..."
    assert request.memo is None

    request_with_memo = SetRefundAddressRequest(address="0x...", memo="12345")
    assert request_with_memo.memo == "12345"


def test_cancel_order_request_model():
    """Test CancelOrderRequest model validation."""
    request = CancelOrderRequest(order_id="test-order-id")
    assert request.order_id == "test-order-id"
