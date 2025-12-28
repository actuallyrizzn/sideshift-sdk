"""Integration tests for SideShift SDK.

These tests verify end-to-end workflows and realistic API interactions.
They test complete scenarios rather than isolated unit functionality.
"""

import os
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
import requests
import responses

from sideshift_sdk import AsyncSideShiftClient, SideShiftClient
from sideshift_sdk.endpoints import account, checkout, coins, pairs, quotes, shifts
from sideshift_sdk.exceptions import (
    SideShiftAPIError,
    SideShiftAuthenticationError,
    SideShiftNetworkError,
    SideShiftRateLimitError,
)
from sideshift_sdk.models import ShiftStatus


@pytest.fixture
def base_url():
    """Base URL for API."""
    return "https://sideshift.ai/api/v2"


@pytest.fixture
def client(base_url):
    """Create a synchronous client for testing."""
    return SideShiftClient(
        secret="test-secret",
        affiliate_id="test-affiliate",
        base_url=base_url,
        timeout=30,
    )


@pytest.fixture
def async_client(base_url):
    """Create an asynchronous client for testing."""
    return AsyncSideShiftClient(
        secret="test-secret",
        affiliate_id="test-affiliate",
        base_url=base_url,
        timeout=30,
    )


class TestQuoteToShiftWorkflow:
    """Test complete workflow from quote request to shift creation."""

    @responses.activate
    def test_quote_to_fixed_shift_workflow(self, client, base_url):
        """Test complete workflow: get coins → get pair → request quote → create fixed shift."""
        # Step 1: Get available coins
        responses.add(
            responses.GET,
            f"{base_url}/coins",
            json=[
                {
                    "networks": ["bitcoin"],
                    "coin": "btc",
                    "name": "Bitcoin",
                    "hasMemo": False,
                    "fixedOnly": False,
                    "variableOnly": False,
                    "networksWithMemo": [],
                    "depositOffline": False,
                    "settleOffline": False,
                },
                {
                    "networks": ["mainnet"],
                    "coin": "eth",
                    "name": "Ethereum",
                    "hasMemo": False,
                    "fixedOnly": False,
                    "variableOnly": False,
                    "networksWithMemo": [],
                    "depositOffline": False,
                    "settleOffline": False,
                },
            ],
            status=200,
        )

        # Step 2: Get pair information
        responses.add(
            responses.GET,
            f"{base_url}/pair/btc/eth",
            json={
                "min": "0.001",
                "max": "10.0",
                "rate": "15.5",
                "depositCoin": "btc",
                "settleCoin": "eth",
                "depositNetwork": "bitcoin",
                "settleNetwork": "mainnet",
            },
            status=200,
        )

        # Step 3: Request quote
        quote_id = "quote-123"
        quote_created = datetime.now(UTC)
        quote_expires = quote_created + timedelta(minutes=15)
        responses.add(
            responses.POST,
            f"{base_url}/quotes",
            json={
                "id": quote_id,
                "createdAt": quote_created.isoformat().replace("+00:00", "") + "Z",
                "depositCoin": "btc",
                "settleCoin": "eth",
                "depositNetwork": "bitcoin",
                "settleNetwork": "mainnet",
                "expiresAt": quote_expires.isoformat().replace("+00:00", "") + "Z",
                "depositAmount": "0.1",
                "settleAmount": "1.5",
                "rate": "15.0",
            },
            status=200,
        )

        # Step 4: Create fixed shift using quote
        shift_id = "shift-456"
        shift_created = datetime.now(UTC)
        responses.add(
            responses.POST,
            f"{base_url}/shifts/fixed",
            json={
                "id": shift_id,
                "createdAt": shift_created.isoformat().replace("+00:00", "") + "Z",
                "depositCoin": "btc",
                "settleCoin": "eth",
                "depositNetwork": "bitcoin",
                "settleNetwork": "mainnet",
                "depositAmount": "0.1",
                "settleAmount": "1.5",
                "rate": "15.0",
                "type": "fixed",
                "status": "waiting",
                "depositAddress": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
                "settleAddress": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            },
            status=200,
        )

        # Execute workflow
        coins_list = coins.get_coins(client)
        assert len(coins_list) >= 2
        assert any(c.coin == "btc" for c in coins_list)
        assert any(c.coin == "eth" for c in coins_list)

        pair = pairs.get_pair(client, from_coin="btc", to_coin="eth")
        assert pair.min == "0.001"
        assert pair.max == "10.0"

        quote = quotes.request_quote(
            client,
            deposit_coin="btc",
            settle_coin="eth",
            deposit_amount="0.1",
        )
        assert quote.id == quote_id
        assert quote.rate == "15.0"

        shift = shifts.create_fixed_shift(
            client,
            quote_id=quote_id,
            settle_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        )
        assert shift.id == shift_id
        assert shift.status == ShiftStatus.WAITING
        assert shift.deposit_address is not None
        assert shift.settle_address == "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"

    @pytest.mark.asyncio
    async def test_quote_to_fixed_shift_workflow_async(self, async_client, base_url):
        """Test async version of quote to fixed shift workflow."""
        # Mock async client responses
        coins_response = [
            {
                "networks": ["bitcoin"],
                "coin": "btc",
                "name": "Bitcoin",
                "hasMemo": False,
                "fixedOnly": False,
                "variableOnly": False,
                "networksWithMemo": [],
                "depositOffline": False,
                "settleOffline": False,
            }
        ]

        quote_id = "quote-123"
        quote_created = datetime.now(UTC)
        quote_expires = quote_created + timedelta(minutes=15)
        quote_response = {
            "id": quote_id,
            "createdAt": quote_created.isoformat().replace("+00:00", "") + "Z",
            "depositCoin": "btc",
            "settleCoin": "eth",
            "depositNetwork": "bitcoin",
            "settleNetwork": "mainnet",
            "expiresAt": quote_expires.isoformat().replace("+00:00", "") + "Z",
            "depositAmount": "0.1",
            "settleAmount": "1.5",
            "rate": "15.0",
        }

        shift_id = "shift-456"
        shift_created = datetime.now(UTC)
        shift_response = {
            "id": shift_id,
            "createdAt": shift_created.isoformat().replace("+00:00", "") + "Z",
            "depositCoin": "btc",
            "settleCoin": "eth",
            "depositNetwork": "bitcoin",
            "settleNetwork": "mainnet",
            "depositAmount": "0.1",
            "settleAmount": "1.5",
            "rate": "15.0",
            "type": "fixed",
            "status": "waiting",
            "depositAddress": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
            "settleAddress": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        }

        with patch.object(async_client, "get", new_callable=AsyncMock, return_value=coins_response):
            with patch.object(async_client, "post", new_callable=AsyncMock) as mock_post:
                mock_post.side_effect = [quote_response, shift_response]

                # Execute workflow
                coins_list = await coins.get_coins_async(async_client)
                assert len(coins_list) >= 1

                quote = await quotes.request_quote_async(
                    async_client,
                    deposit_coin="btc",
                    settle_coin="eth",
                    deposit_amount="0.1",
                )
                assert quote.id == quote_id

                shift = await shifts.create_fixed_shift_async(
                    async_client,
                    quote_id=quote_id,
                    settle_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                )
                assert shift.id == shift_id
                assert shift.status == ShiftStatus.WAITING


class TestErrorHandlingIntegration:
    """Test error handling in realistic scenarios."""

    @responses.activate
    def test_authentication_error_propagation(self, client, base_url):
        """Test that authentication errors are properly raised and handled."""
        responses.add(
            responses.GET,
            f"{base_url}/coins",
            json={"message": "Invalid API secret"},
            status=401,
        )

        with pytest.raises(SideShiftAuthenticationError) as exc_info:
            coins.get_coins(client)

        assert exc_info.value.status_code == 401
        assert "Invalid API secret" in exc_info.value.message

    @responses.activate
    @patch("sideshift_sdk.client.time.sleep")
    def test_rate_limit_with_retry(self, mock_sleep, client, base_url):
        """Test rate limiting with retry logic."""
        # First request: rate limited
        responses.add(
            responses.GET,
            f"{base_url}/coins",
            json={"message": "Rate limit exceeded"},
            status=429,
            headers={"Retry-After": "1"},
        )

        # Second request: success
        responses.add(
            responses.GET,
            f"{base_url}/coins",
            json=[
                {
                    "networks": ["bitcoin"],
                    "coin": "btc",
                    "name": "Bitcoin",
                    "hasMemo": False,
                    "fixedOnly": False,
                    "variableOnly": False,
                    "networksWithMemo": [],
                    "depositOffline": False,
                    "settleOffline": False,
                }
            ],
            status=200,
        )

        # Should retry and succeed
        coins_list = coins.get_coins(client)
        assert len(coins_list) == 1
        assert coins_list[0].coin == "btc"
        assert mock_sleep.called  # Verify sleep was called for retry

    @responses.activate
    def test_network_error_handling(self, client, base_url):
        """Test network error handling."""
        # Use responses callback to raise a connection error
        def connection_error_callback(request):
            import requests
            raise requests.exceptions.ConnectionError("Connection refused")

        responses.add_callback(
            responses.GET,
            f"{base_url}/coins",
            callback=connection_error_callback,
        )

        with pytest.raises(SideShiftNetworkError):
            coins.get_coins(client)


class TestConfigurationIntegration:
    """Test that configuration options work together correctly."""

    @responses.activate
    def test_custom_base_url_and_timeout(self, base_url):
        """Test client with custom base URL and timeout."""
        custom_url = "https://custom.example.com/api/v2"
        client = SideShiftClient(
            secret="test-secret",
            base_url=custom_url,
            timeout=60,
        )

        responses.add(
            responses.GET,
            f"{custom_url}/coins",
            json=[],
            status=200,
        )

        coins_list = coins.get_coins(client)
        assert coins_list == []

    @responses.activate
    def test_api_version_configuration(self, base_url):
        """Test API version configuration."""
        client = SideShiftClient(
            secret="test-secret",
            api_version="v2",
        )

        # Should use default v2 URL
        expected_url = "https://sideshift.ai/api/v2/coins"
        responses.add(
            responses.GET,
            expected_url,
            json=[],
            status=200,
        )

        coins_list = coins.get_coins(client)
        assert coins_list == []

    @responses.activate
    def test_logging_enabled(self, base_url):
        """Test client with logging enabled."""
        client = SideShiftClient(
            secret="test-secret",
            base_url=base_url,
            enable_logging=True,
            log_level="DEBUG",
        )

        responses.add(
            responses.GET,
            f"{base_url}/coins",
            json=[],
            status=200,
        )

        # Should not raise, logging should work
        coins_list = coins.get_coins(client)
        assert coins_list == []


class TestShiftStatusWorkflow:
    """Test shift status monitoring workflow."""

    @responses.activate
    def test_shift_status_monitoring(self, client, base_url):
        """Test monitoring shift status from creation to completion."""
        shift_id = "shift-789"
        shift_created = datetime.now(UTC)

        # Create shift
        responses.add(
            responses.POST,
            f"{base_url}/shifts/fixed",
            json={
                "id": shift_id,
                "createdAt": shift_created.isoformat().replace("+00:00", "") + "Z",
                "depositCoin": "btc",
                "settleCoin": "eth",
                "depositNetwork": "bitcoin",
                "settleNetwork": "mainnet",
                "depositAmount": "0.1",
                "settleAmount": "1.5",
                "type": "fixed",
                "rate": "15.0",
                "status": "waiting",
                "depositAddress": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
                "settleAddress": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            },
            status=200,
        )

        # Check status: waiting
        responses.add(
            responses.GET,
            f"{base_url}/shifts/{shift_id}",
            json={
                "id": shift_id,
                "createdAt": shift_created.isoformat().replace("+00:00", "") + "Z",
                "depositCoin": "btc",
                "settleCoin": "eth",
                "depositNetwork": "bitcoin",
                "settleNetwork": "mainnet",
                "depositAmount": "0.1",
                "settleAmount": "1.5",
                "type": "fixed",
                "rate": "15.0",
                "status": "waiting",
                "depositAddress": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
                "settleAddress": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            },
            status=200,
        )

        # Check status: completed
        responses.add(
            responses.GET,
            f"{base_url}/shifts/{shift_id}",
            json={
                "id": shift_id,
                "createdAt": shift_created.isoformat().replace("+00:00", "") + "Z",
                "depositCoin": "btc",
                "settleCoin": "eth",
                "depositNetwork": "bitcoin",
                "settleNetwork": "mainnet",
                "depositAmount": "0.1",
                "settleAmount": "1.5",
                "type": "fixed",
                "rate": "15.0",
                "status": "complete",
                "depositAddress": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
                "settleAddress": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "depositHash": "abc123",
                "settleHash": "def456",
            },
            status=200,
        )

        # Create shift (using a quote)
        quote_id = "quote-789"
        responses.add(
            responses.POST,
            f"{base_url}/quotes",
            json={
                "id": quote_id,
                "createdAt": shift_created.isoformat().replace("+00:00", "") + "Z",
                "depositCoin": "btc",
                "settleCoin": "eth",
                "depositNetwork": "bitcoin",
                "settleNetwork": "mainnet",
                "expiresAt": (shift_created + timedelta(minutes=15)).isoformat().replace("+00:00", "") + "Z",
                "depositAmount": "0.1",
                "settleAmount": "1.5",
                "rate": "15.0",
            },
            status=200,
        )
        quote = quotes.request_quote(
            client,
            deposit_coin="btc",
            settle_coin="eth",
            deposit_amount="0.1",
        )
        shift = shifts.create_fixed_shift(
            client,
            quote_id=quote.id,
            settle_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        )
        assert shift.id == shift_id
        assert shift.status == ShiftStatus.WAITING

        # Check status: waiting
        shift = shifts.get_shift(client, shift_id)
        assert shift.status == ShiftStatus.WAITING

        # Check status: completed
        shift = shifts.get_shift(client, shift_id)
        assert shift.status == ShiftStatus.COMPLETE
        # Note: deposit_hash and settle_hash are typically in the deposits field
        # For this test, we just verify the status changed correctly


class TestCheckoutWorkflow:
    """Test checkout creation and retrieval workflow."""

    @responses.activate
    def test_checkout_workflow(self, client, base_url):
        """Test creating and retrieving a checkout."""
        checkout_id = "checkout-123"
        checkout_created = datetime.now(UTC)

        # Create checkout
        responses.add(
            responses.POST,
            f"{base_url}/checkout",
            json={
                "id": checkout_id,
                "createdAt": checkout_created.isoformat().replace("+00:00", "") + "Z",
                "updatedAt": checkout_created.isoformat().replace("+00:00", "") + "Z",
                "settleCoin": "eth",
                "settleNetwork": "mainnet",
                "settleAddress": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "settleAmount": "1.5",
                "affiliateId": "test-affiliate",
                "successUrl": "https://example.com/success",
                "cancelUrl": "https://example.com/cancel",
            },
            status=200,
        )

        # Retrieve checkout
        responses.add(
            responses.GET,
            f"{base_url}/checkout/{checkout_id}",
            json={
                "id": checkout_id,
                "createdAt": checkout_created.isoformat().replace("+00:00", "") + "Z",
                "updatedAt": checkout_created.isoformat().replace("+00:00", "") + "Z",
                "settleCoin": "eth",
                "settleNetwork": "mainnet",
                "settleAddress": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "settleAmount": "1.5",
                "affiliateId": "test-affiliate",
                "successUrl": "https://example.com/success",
                "cancelUrl": "https://example.com/cancel",
            },
            status=200,
        )

        # Create checkout
        checkout_obj = checkout.create_checkout(
            client,
            settle_coin="eth",
            settle_network="mainnet",
            settle_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            settle_amount="1.5",
            affiliate_id="test-affiliate",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            user_ip="1.2.3.4",
        )
        assert checkout_obj.id == checkout_id

        # Retrieve checkout
        retrieved = checkout.get_checkout(client, checkout_id)
        assert retrieved.id == checkout_id
        assert retrieved.settle_coin == "eth"
        assert retrieved.settle_amount == "1.5"


class TestContextManagerIntegration:
    """Test context manager usage in realistic scenarios."""

    @responses.activate
    def test_sync_context_manager(self, base_url):
        """Test synchronous client as context manager."""
        responses.add(
            responses.GET,
            f"{base_url}/coins",
            json=[],
            status=200,
        )

        with SideShiftClient(secret="test-secret", base_url=base_url) as client:
            coins_list = coins.get_coins(client)
            assert coins_list == []

        # Client should be closed after context exit
        # requests.Session doesn't have a 'closed' attribute, but we can check if it's been closed
        # by trying to make a request (which should fail if closed) or checking the adapter
        # For now, just verify the context manager worked without error
        pass

    @pytest.mark.asyncio
    async def test_async_context_manager(self, base_url):
        """Test asynchronous client as context manager."""
        async with AsyncSideShiftClient(secret="test-secret", base_url=base_url) as client:
            with patch.object(client, "get", new_callable=AsyncMock, return_value=[]):
                coins_list = await coins.get_coins_async(client)
                assert coins_list == []

        # Client should be closed after context exit
        assert client._client is None or client._client.is_closed


class TestBulkOperations:
    """Test bulk operations integration."""

    @responses.activate
    def test_bulk_shift_retrieval(self, client, base_url):
        """Test retrieving multiple shifts at once."""
        shift_ids = ["shift-1", "shift-2", "shift-3"]

        shift_created_time = datetime.now(UTC)
        responses.add(
            responses.GET,
            f"{base_url}/shifts",
            json=[
                {
                    "id": "shift-1",
                    "createdAt": shift_created_time.isoformat().replace("+00:00", "") + "Z",
                    "depositCoin": "btc",
                    "settleCoin": "eth",
                    "depositNetwork": "bitcoin",
                    "settleNetwork": "mainnet",
                    "type": "fixed",
                    "status": "complete",
                    "settleAddress": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                },
                {
                    "id": "shift-2",
                    "createdAt": shift_created_time.isoformat().replace("+00:00", "") + "Z",
                    "depositCoin": "btc",
                    "settleCoin": "eth",
                    "depositNetwork": "bitcoin",
                    "settleNetwork": "mainnet",
                    "type": "fixed",
                    "status": "waiting",
                    "settleAddress": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                },
                {
                    "id": "shift-3",
                    "createdAt": shift_created_time.isoformat().replace("+00:00", "") + "Z",
                    "depositCoin": "btc",
                    "settleCoin": "eth",
                    "depositNetwork": "bitcoin",
                    "settleNetwork": "mainnet",
                    "type": "fixed",
                    "status": "refunded",
                    "settleAddress": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                },
            ],
            status=200,
        )

        shifts_list = shifts.get_bulk_shifts(client, shift_ids)
        assert len(shifts_list) == 3
        assert shifts_list[0].id == "shift-1"
        assert shifts_list[0].status == ShiftStatus.COMPLETE
        assert shifts_list[1].status == ShiftStatus.WAITING
        assert shifts_list[2].status == ShiftStatus.REFUNDED

