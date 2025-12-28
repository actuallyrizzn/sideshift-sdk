"""Async usage examples for SideShift SDK."""

import asyncio

from sideshift_sdk import AsyncSideShiftClient
from sideshift_sdk.endpoints import account, coins, pairs, quotes, shifts


async def example_get_coins_async():
    """Example: Get all available coins (async)."""
    async with AsyncSideShiftClient() as client:
        coins_list = await coins.get_coins_async(client)
        print(f"Found {len(coins_list)} coins")

        for coin in coins_list[:5]:
            print(f"  - {coin.coin} ({coin.name}) on {coin.networks}")


async def example_fixed_shift_async():
    """Example: Create a fixed rate shift (async)."""
    async with AsyncSideShiftClient(
        secret="your-secret-key",
        affiliate_id="your-affiliate-id",
    ) as client:
        # Step 1: Request a quote
        quote = await quotes.request_quote_async(
            client,
            deposit_coin="btc",
            settle_coin="eth",
            deposit_amount="0.1",
            deposit_network="bitcoin",
            settle_network="mainnet",
        )

        print(f"Quote ID: {quote.id}")
        print(f"Rate: {quote.rate}")

        # Step 2: Create the shift
        shift = await shifts.create_fixed_shift_async(
            client,
            quote_id=quote.id,
            settle_address="0xde2642b2120fd3011fe9659688f76e9E4676F472",
        )

        print(f"Shift created! ID: {shift.id}")
        print(f"Deposit Address: {shift.deposit_address}")

        # Step 3: Monitor the shift
        while shift.status not in ["complete", "refunded", "expired"]:
            await asyncio.sleep(10)  # Poll every 10 seconds

            shift = await shifts.get_shift_async(client, shift_id=shift.id)
            print(f"Status: {shift.status}")


async def example_multiple_operations():
    """Example: Perform multiple operations concurrently."""
    async with AsyncSideShiftClient(
        secret="your-secret-key",
        affiliate_id="your-affiliate-id",
    ) as client:
        # Run multiple operations concurrently
        coins_task = coins.get_coins_async(client)
        account_task = account.get_account(client)
        xai_stats_task = account.get_xai_stats_async(client)

        coins_list, account_info, xai_stats = await asyncio.gather(
            coins_task,
            account_task,
            xai_stats_task,
        )

        print(f"Coins: {len(coins_list)}")
        print(f"Account Balance: {account_info.total_balance}")
        print(f"XAI Price: ${xai_stats.xai_price_usd}")


if __name__ == "__main__":
    # Run examples
    # asyncio.run(example_get_coins_async())
    # asyncio.run(example_fixed_shift_async())
    # asyncio.run(example_multiple_operations())
    pass

