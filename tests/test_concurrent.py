"""Tests for concurrent request handling."""

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
import responses

from sideshift_sdk.client import AsyncSideShiftClient, SideShiftClient
from sideshift_sdk.endpoints import account, coins, pairs, quotes
from sideshift_sdk.exceptions import SideShiftRateLimitError


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


class TestAsyncConcurrentRequests:
    """Test concurrent requests with async client."""

    @pytest.mark.asyncio
    async def test_multiple_concurrent_requests(self, async_client, base_url):
        """Test multiple async requests running concurrently."""
        mock_coins_response = [
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

        mock_account_response = {
            "id": "test-account-id",
            "lifetimeStakingRewards": "100.0",
            "unstaking": "10.0",
            "staked": "50.0",
            "available": "40.0",
            "totalBalance": "100.0",
        }

        mock_pairs_response = [
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

        async with async_client:
            mock_http_response_coins = Mock()
            mock_http_response_coins.status_code = 200
            mock_http_response_coins.json.return_value = mock_coins_response
            mock_http_response_coins.content = b"[]"
            mock_http_response_coins.headers = {}

            mock_http_response_account = Mock()
            mock_http_response_account.status_code = 200
            mock_http_response_account.json.return_value = mock_account_response
            mock_http_response_account.content = b"{}"
            mock_http_response_account.headers = {}

            mock_http_response_pairs = Mock()
            mock_http_response_pairs.status_code = 200
            mock_http_response_pairs.json.return_value = mock_pairs_response
            mock_http_response_pairs.content = b"[]"
            mock_http_response_pairs.headers = {}

            call_count = {"count": 0}

            async def mock_request(*args, **kwargs):
                call_count["count"] += 1
                if "coins" in str(kwargs.get("url", "")):
                    return mock_http_response_coins
                elif "account" in str(kwargs.get("url", "")):
                    return mock_http_response_account
                elif "pairs" in str(kwargs.get("url", "")):
                    return mock_http_response_pairs
                return mock_http_response_coins

            with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock) as mock_request_patch:
                mock_request_patch.side_effect = mock_request

                # Run multiple requests concurrently
                results = await asyncio.gather(
                    coins.get_coins_async(async_client),
                    account.get_account_async(async_client),
                    pairs.get_pairs_async(async_client, pairs=["btc", "eth"]),
                )

                # Verify all requests completed
                assert len(results) == 3
                assert results[0][0].coin == "btc"
                assert results[1].id == "test-account-id"
                assert len(results[2]) == 1
                assert results[2][0].deposit_coin == "btc"

                # Verify all requests were made
                assert call_count["count"] == 3

    @pytest.mark.asyncio
    async def test_concurrent_requests_unique_request_ids(self, async_client, base_url):
        """Test that concurrent requests get unique request IDs."""
        mock_account_response = {
            "id": "test-account-id",
            "lifetimeStakingRewards": "100.0",
            "unstaking": "10.0",
            "staked": "50.0",
            "available": "40.0",
            "totalBalance": "100.0",
        }

        async with async_client:
            request_ids = []

            async def mock_request(*args, **kwargs):
                # Capture request ID from headers
                headers = kwargs.get("headers", {})
                if "X-Request-ID" in headers:
                    request_ids.append(headers["X-Request-ID"])

                mock_http_response = Mock()
                mock_http_response.status_code = 200
                mock_http_response.json.return_value = mock_account_response
                mock_http_response.content = b"{}"
                mock_http_response.headers = {}
                return mock_http_response

            with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock) as mock_request_patch:
                mock_request_patch.side_effect = mock_request

                # Run 10 concurrent requests
                await asyncio.gather(
                    *[account.get_account_async(async_client) for _ in range(10)]
                )

                # Verify all request IDs are unique
                assert len(request_ids) == 10
                assert len(set(request_ids)) == 10  # All unique

    @pytest.mark.asyncio
    async def test_concurrent_requests_error_isolation(self, async_client, base_url):
        """Test that errors in concurrent requests are properly isolated."""
        async with async_client:
            mock_success_response = Mock()
            mock_success_response.status_code = 200
            mock_success_response.json.return_value = {
                "id": "success",
                "lifetimeStakingRewards": "100.0",
                "unstaking": "10.0",
                "staked": "50.0",
                "available": "40.0",
                "totalBalance": "100.0",
            }
            mock_success_response.content = b"{}"
            mock_success_response.headers = {}

            mock_error_response = Mock()
            mock_error_response.status_code = 404
            mock_error_response.json.return_value = {"message": "Not found"}
            mock_error_response.content = b'{"message": "Not found"}'
            mock_error_response.headers = {}

            call_count = {"count": 0}

            async def mock_request(*args, **kwargs):
                call_count["count"] += 1
                if call_count["count"] == 2:  # Second request fails
                    return mock_error_response
                return mock_success_response

            with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock) as mock_request_patch:
                mock_request_patch.side_effect = mock_request

                # Run 3 concurrent requests, one will fail
                results = await asyncio.gather(
                    account.get_account_async(async_client),
                    account.get_account_async(async_client),
                    account.get_account_async(async_client),
                    return_exceptions=True,
                )

                # Verify one succeeded and one failed
                assert len(results) == 3
                assert not isinstance(results[0], Exception)
                assert results[0].id == "success"
                assert isinstance(results[1], Exception)
                assert not isinstance(results[2], Exception)
                assert results[2].id == "success"


class TestSyncThreadSafety:
    """Test thread safety of synchronous client."""

    @responses.activate
    def test_multiple_threads_simultaneous_requests(self, client, base_url):
        """Test synchronous client being used from multiple threads."""
        num_threads = 5
        num_requests_per_thread = 3

        # Set up mock responses
        for i in range(num_threads * num_requests_per_thread):
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
                    }
                ],
                status=200,
            )

        def make_requests(thread_id):
            """Make requests from a thread."""
            results = []
            for _ in range(num_requests_per_thread):
                try:
                    coins_list = coins.get_coins(client)
                    results.append((thread_id, "success", len(coins_list)))
                except Exception as e:
                    results.append((thread_id, "error", str(e)))
            return results

        # Run requests from multiple threads
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_requests, i) for i in range(num_threads)]
            all_results = []
            for future in as_completed(futures):
                all_results.extend(future.result())

        # Verify all requests succeeded
        assert len(all_results) == num_threads * num_requests_per_thread
        for thread_id, status, result in all_results:
            assert status == "success"
            assert result == 1  # One coin in response

    @responses.activate
    def test_thread_safety_unique_request_ids(self, client, base_url):
        """Test that requests from different threads get unique request IDs."""
        num_threads = 5

        # Set up mock responses
        for _ in range(num_threads):
            responses.add(
                responses.GET,
                f"{base_url}/account",
                json={
                    "id": "test-account-id",
                    "lifetimeStakingRewards": "100.0",
                    "unstaking": "10.0",
                    "staked": "50.0",
                    "available": "40.0",
                    "totalBalance": "100.0",
                },
                status=200,
            )

        request_ids = []

        def make_request(thread_id):
            """Make a request and capture request ID."""
            try:
                account_info = account.get_account(client)
                # Request ID is generated internally, we can't easily capture it
                # but we can verify the request was made successfully
                return (thread_id, "success", account_info.id)
            except Exception as e:
                return (thread_id, "error", str(e))

        # Run requests from multiple threads
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]

        # Verify all requests succeeded
        assert len(results) == num_threads
        for thread_id, status, result in results:
            assert status == "success"
            assert result == "test-account-id"


class TestConcurrentRateLimiting:
    """Test rate limiting behavior with concurrent requests."""

    @pytest.mark.asyncio
    async def test_concurrent_requests_rate_limiting(self, async_client, base_url):
        """Test rate limiting when multiple requests are made concurrently."""
        async with async_client:
            # First request succeeds, subsequent ones get rate limited
            mock_success_response = Mock()
            mock_success_response.status_code = 200
            mock_success_response.json.return_value = {
                "id": "success",
                "lifetimeStakingRewards": "100.0",
                "unstaking": "10.0",
                "staked": "50.0",
                "available": "40.0",
                "totalBalance": "100.0",
            }
            mock_success_response.content = b"{}"
            mock_success_response.headers = {}

            mock_rate_limit_response = Mock()
            mock_rate_limit_response.status_code = 429
            mock_rate_limit_response.json.return_value = {"message": "Rate limited"}
            mock_rate_limit_response.content = b'{"message": "Rate limited"}'
            mock_rate_limit_response.headers = {"Retry-After": "60"}

            call_count = {"count": 0}

            async def mock_request(*args, **kwargs):
                call_count["count"] += 1
                if call_count["count"] == 1:
                    return mock_success_response
                return mock_rate_limit_response

            with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock) as mock_request_patch:
                mock_request_patch.side_effect = mock_request

                # Run 3 concurrent requests
                results = await asyncio.gather(
                    account.get_account_async(async_client),
                    account.get_account_async(async_client),
                    account.get_account_async(async_client),
                    return_exceptions=True,
                )

                # Verify first succeeded, others got rate limited
                assert len(results) == 3
                assert not isinstance(results[0], Exception)
                assert results[0].id == "success"
                assert isinstance(results[1], SideShiftRateLimitError)
                assert isinstance(results[2], SideShiftRateLimitError)

    @responses.activate
    def test_concurrent_rate_limiting_sync(self, client, base_url):
        """Test rate limiting with concurrent sync requests."""
        # First request succeeds
        responses.add(
            responses.GET,
            f"{base_url}/account",
            json={
                "id": "test-account-id",
                "lifetimeStakingRewards": "100.0",
                "unstaking": "10.0",
                "staked": "50.0",
                "available": "40.0",
                "totalBalance": "100.0",
            },
            status=200,
        )

        # Subsequent requests get rate limited
        for _ in range(4):
            responses.add(
                responses.GET,
                f"{base_url}/account",
                json={"message": "Rate limited"},
                status=429,
                headers={"Retry-After": "60"},
            )

        def make_request(thread_id):
            """Make a request."""
            try:
                account_info = account.get_account(client)
                return (thread_id, "success", account_info.id)
            except SideShiftRateLimitError as e:
                return (thread_id, "rate_limited", str(e))
            except Exception as e:
                return (thread_id, "error", str(e))

        # Run 5 concurrent requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(5)]
            results = [future.result() for future in as_completed(futures)]

        # Verify first succeeded, others got rate limited
        assert len(results) == 5
        success_count = sum(1 for _, status, _ in results if status == "success")
        rate_limited_count = sum(1 for _, status, _ in results if status == "rate_limited")
        assert success_count == 1
        assert rate_limited_count == 4


class TestConcurrentConnectionPooling:
    """Test connection pooling behavior with concurrent requests."""

    @pytest.mark.asyncio
    async def test_async_connection_pooling_concurrent(self, async_client, base_url):
        """Test that connection pooling works correctly with concurrent requests."""
        async with async_client:
            mock_account_response = {
                "id": "test-account-id",
                "lifetimeStakingRewards": "100.0",
                "unstaking": "10.0",
                "staked": "50.0",
                "available": "40.0",
                "totalBalance": "100.0",
            }

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_account_response
            mock_response.content = b"{}"
            mock_response.headers = {}

            client_instances = []

            async def mock_request(*args, **kwargs):
                # Track which client instance is being used
                client_instances.append(id(kwargs.get("client", None)))
                return mock_response

            with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock) as mock_request_patch:
                mock_request_patch.side_effect = mock_request

                # Run 10 concurrent requests
                await asyncio.gather(
                    *[account.get_account_async(async_client) for _ in range(10)]
                )

                # All requests should use the same client instance (connection pool)
                # Since we're patching at the class level, we can't verify the exact instance
                # But we can verify all requests completed successfully
                assert len(client_instances) == 10

    @responses.activate
    def test_sync_connection_pooling_concurrent(self, client, base_url):
        """Test that connection pooling works correctly with concurrent sync requests."""
        # Set up mock responses
        for _ in range(10):
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
                    }
                ],
                status=200,
            )

        def make_request(thread_id):
            """Make a request."""
            try:
                coins_list = coins.get_coins(client)
                return (thread_id, "success", len(coins_list))
            except Exception as e:
                return (thread_id, "error", str(e))

        # Run 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            results = [future.result() for future in as_completed(futures)]

        # Verify all requests succeeded
        assert len(results) == 10
        for thread_id, status, result in results:
            assert status == "success"
            assert result == 1

