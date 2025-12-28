"""Async usage examples for SideShift SDK."""

import asyncio

from sideshift_sdk import AsyncSideShiftClient
from sideshift_sdk.endpoints import account, checkout, coins, pairs, quotes, shifts


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
        account_task = account.get_account_async(client)
        xai_stats_task = account.get_xai_stats_async(client)

        coins_list, account_info, xai_stats = await asyncio.gather(
            coins_task,
            account_task,
            xai_stats_task,
        )

        print(f"Coins: {len(coins_list)}")
        print(f"Account Balance: {account_info.total_balance}")
        print(f"XAI Price: ${xai_stats.xai_price_usd}")


async def example_get_pairs_async():
    """Example: Get multiple pairs information (async)."""
    async with AsyncSideShiftClient(
        secret="your-secret-key",
        affiliate_id="your-affiliate-id",
    ) as client:
        pairs_list = await pairs.get_pairs_async(
            client,
            pairs=["btc-mainnet", "eth-mainnet", "usdc-bsc"],
        )

        for pair in pairs_list:
            print(f"{pair.from_coin} -> {pair.to_coin}")
            print(f"  Rate: {pair.rate}, Min: {pair.min}, Max: {pair.max}")


async def example_get_shift_async():
    """Example: Get shift information (async)."""
    async with AsyncSideShiftClient() as client:
        shift = await shifts.get_shift_async(client, shift_id="your-shift-id")

        print(f"Shift ID: {shift.id}")
        print(f"Status: {shift.status}")
        print(f"Deposit Address: {shift.deposit_address}")


async def example_get_bulk_shifts_async():
    """Example: Get multiple shifts (async)."""
    async with AsyncSideShiftClient() as client:
        shift_ids = ["shift-id-1", "shift-id-2", "shift-id-3"]
        shifts_list = await shifts.get_bulk_shifts_async(client, shift_ids=shift_ids)

        for shift in shifts_list:
            print(f"{shift.id}: {shift.status}")


async def example_get_recent_shifts_async():
    """Example: Get recent completed shifts (async)."""
    async with AsyncSideShiftClient() as client:
        recent_shifts = await shifts.get_recent_shifts_async(client, limit=10)

        print(f"Found {len(recent_shifts)} recent shifts")
        for shift in recent_shifts:
            print(f"  {shift.id}: {shift.status}")


async def example_set_refund_address_async():
    """Example: Set refund address for a shift (async)."""
    async with AsyncSideShiftClient(secret="your-secret-key") as client:
        updated_shift = await shifts.set_refund_address_async(
            client,
            shift_id="your-shift-id",
            address="0x...",
            memo="optional-memo",
        )

        print(f"Refund address updated for shift {updated_shift.id}")


async def example_cancel_order_async():
    """Example: Cancel an order (async)."""
    async with AsyncSideShiftClient(secret="your-secret-key") as client:
        await shifts.cancel_order_async(client, order_id="your-order-id")
        print("Order cancelled successfully")


async def example_get_permissions_async():
    """Example: Check permissions (async)."""
    async with AsyncSideShiftClient(user_ip="1.2.3.4") as client:
        permissions = await account.get_permissions_async(client, user_ip="1.2.3.4")

        print(f"Can create shifts: {permissions.can_create_shifts}")
        print(f"Can create checkouts: {permissions.can_create_checkouts}")


async def example_get_xai_stats_async():
    """Example: Get XAI statistics (async)."""
    async with AsyncSideShiftClient() as client:
        xai_stats = await account.get_xai_stats_async(client)

        print(f"XAI Price (USD): ${xai_stats.xai_price_usd}")
        print(f"XAI Supply: {xai_stats.xai_supply}")


async def example_get_coin_icon_async():
    """Example: Get coin icon (async)."""
    async with AsyncSideShiftClient() as client:
        # Get coin icon as SVG
        icon_svg = await coins.get_coin_icon_async(client, coin_network="btc", format="svg")

        # Get coin icon as PNG
        icon_png = await coins.get_coin_icon_async(client, coin_network="eth", format="png")

        # Save icon to file
        with open("btc-icon.svg", "wb") as f:
            f.write(icon_svg)

        with open("eth-icon.png", "wb") as f:
            f.write(icon_png)

        print("Icons saved successfully")


async def example_get_checkout_async():
    """Example: Get checkout information (async)."""
    async with AsyncSideShiftClient() as client:
        checkout_info = await checkout.get_checkout_async(client, checkout_id="your-checkout-id")

        print(f"Checkout ID: {checkout_info.id}")
        print(f"Settle Coin: {checkout_info.settle_coin}")
        print(f"Settle Amount: {checkout_info.settle_amount}")


async def example_create_checkout_async():
    """Example: Create a checkout (async)."""
    async with AsyncSideShiftClient(
        secret="your-secret-key",
        affiliate_id="your-affiliate-id",
        user_ip="1.2.3.4",
    ) as client:
        checkout_info = await checkout.create_checkout_async(
            client,
            settle_coin="eth",
            settle_network="mainnet",
            settle_amount="1.0",
            settle_address="0x...",
            affiliate_id="your-affiliate-id",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            settle_memo="optional-memo",
        )

        print(f"Checkout created: {checkout_info.id}")
        print(f"Checkout URL: {checkout_info.checkout_url}")


if __name__ == "__main__":
    # Run examples
    # asyncio.run(example_get_coins_async())
    # asyncio.run(example_fixed_shift_async())
    # asyncio.run(example_multiple_operations())
    # asyncio.run(example_get_pairs_async())
    # asyncio.run(example_get_shift_async())
    # asyncio.run(example_get_bulk_shifts_async())
    # asyncio.run(example_get_recent_shifts_async())
    # asyncio.run(example_set_refund_address_async())
    # asyncio.run(example_cancel_order_async())
    # asyncio.run(example_get_permissions_async())
    # asyncio.run(example_get_xai_stats_async())
    # asyncio.run(example_get_coin_icon_async())
    # asyncio.run(example_get_checkout_async())
    # asyncio.run(example_create_checkout_async())
    pass

