"""Basic usage examples for SideShift SDK."""

from sideshift_sdk import SideShiftClient
from sideshift_sdk.endpoints import account, checkout, coins, pairs, quotes, shifts


def example_get_coins():
    """Example: Get all available coins."""
    client = SideShiftClient()

    # Get all coins
    coins_list = coins.get_coins(client)
    print(f"Found {len(coins_list)} coins")

    # Print first few coins
    for coin in coins_list[:5]:
        print(f"  - {coin.coin} ({coin.name}) on {coin.networks}")


def example_get_pair():
    """Example: Get pair information."""
    client = SideShiftClient(
        secret="your-secret-key",
        affiliate_id="your-affiliate-id",
    )

    # Get pair info
    pair = pairs.get_pair(
        client,
        from_coin="btc",
        to_coin="eth",
    )

    print(f"BTC -> ETH")
    print(f"  Rate: {pair.rate}")
    print(f"  Min: {pair.min}")
    print(f"  Max: {pair.max}")


def example_fixed_shift():
    """Example: Create a fixed rate shift."""
    client = SideShiftClient(
        secret="your-secret-key",
        affiliate_id="your-affiliate-id",
    )

    # Step 1: Request a quote
    quote = quotes.request_quote(
        client,
        deposit_coin="btc",
        settle_coin="eth",
        deposit_amount="0.1",
        deposit_network="bitcoin",
        settle_network="mainnet",
    )

    print(f"Quote ID: {quote.id}")
    print(f"Rate: {quote.rate}")
    print(f"Deposit: {quote.deposit_amount} {quote.deposit_coin}")
    print(f"Settle: {quote.settle_amount} {quote.settle_coin}")
    print(f"Expires at: {quote.expires_at}")

    # Step 2: Create the shift
    shift = shifts.create_fixed_shift(
        client,
        quote_id=quote.id,
        settle_address="0xde2642b2120fd3011fe9659688f76e9E4676F472",
    )

    print(f"\nShift created!")
    print(f"Shift ID: {shift.id}")
    print(f"Deposit Address: {shift.deposit_address}")
    print(f"Status: {shift.status}")

    # Step 3: Monitor the shift
    while shift.status not in ["complete", "refunded", "expired"]:
        import time
        time.sleep(10)  # Poll every 10 seconds

        shift = shifts.get_shift(client, shift_id=shift.id)
        print(f"Status: {shift.status}")


def example_variable_shift():
    """Example: Create a variable rate shift."""
    client = SideShiftClient(
        secret="your-secret-key",
        affiliate_id="your-affiliate-id",
    )

    # Create variable shift (no quote needed)
    shift = shifts.create_variable_shift(
        client,
        deposit_coin="btc",
        settle_coin="eth",
        settle_address="0xde2642b2120fd3011fe9659688f76e9E4676F472",
        deposit_network="bitcoin",
        settle_network="mainnet",
    )

    print(f"Variable shift created!")
    print(f"Shift ID: {shift.id}")
    print(f"Deposit Address: {shift.deposit_address}")
    print(f"Status: {shift.status}")


def example_get_account():
    """Example: Get account information."""
    client = SideShiftClient(secret="your-secret-key")

    account_info = account.get_account(client)

    print(f"Account ID: {account_info.id}")
    print(f"Available: {account_info.available}")
    print(f"Staked: {account_info.staked}")
    print(f"Total Balance: {account_info.total_balance}")


def example_get_pairs():
    """Example: Get multiple pairs information."""
    client = SideShiftClient(
        secret="your-secret-key",
        affiliate_id="your-affiliate-id",
    )

    # Get information for multiple pairs
    pairs_list = pairs.get_pairs(
        client,
        pairs=["btc-mainnet", "eth-mainnet", "usdc-bsc"],
    )

    for pair in pairs_list:
        print(f"{pair.from_coin} -> {pair.to_coin}")
        print(f"  Rate: {pair.rate}, Min: {pair.min}, Max: {pair.max}")


def example_get_shift():
    """Example: Get shift information."""
    client = SideShiftClient()

    # Get a specific shift (no auth required for public shifts)
    shift = shifts.get_shift(client, shift_id="your-shift-id")

    print(f"Shift ID: {shift.id}")
    print(f"Status: {shift.status}")
    print(f"Deposit Address: {shift.deposit_address}")
    print(f"Settle Address: {shift.settle_address}")


def example_get_bulk_shifts():
    """Example: Get multiple shifts."""
    client = SideShiftClient()

    # Get multiple shifts by IDs
    shift_ids = ["shift-id-1", "shift-id-2", "shift-id-3"]
    shifts_list = shifts.get_bulk_shifts(client, shift_ids=shift_ids)

    for shift in shifts_list:
        print(f"{shift.id}: {shift.status}")


def example_get_recent_shifts():
    """Example: Get recent completed shifts."""
    client = SideShiftClient()

    # Get recent completed shifts (limit 1-100)
    recent_shifts = shifts.get_recent_shifts(client, limit=10)

    print(f"Found {len(recent_shifts)} recent shifts")
    for shift in recent_shifts:
        print(f"  {shift.id}: {shift.status} - {shift.deposit_coin} -> {shift.settle_coin}")


def example_set_refund_address():
    """Example: Set refund address for a shift."""
    client = SideShiftClient(secret="your-secret-key")

    # Set refund address for a shift
    updated_shift = shifts.set_refund_address(
        client,
        shift_id="your-shift-id",
        address="0x...",
        memo="optional-memo",  # Required for some coins like XRP
    )

    print(f"Refund address updated for shift {updated_shift.id}")


def example_cancel_order():
    """Example: Cancel an order."""
    client = SideShiftClient(secret="your-secret-key")

    # Cancel an order
    shifts.cancel_order(client, order_id="your-order-id")

    print("Order cancelled successfully")


def example_get_permissions():
    """Example: Check permissions."""
    client = SideShiftClient(user_ip="1.2.3.4")

    # Check permissions for creating shifts
    permissions = account.get_permissions(client, user_ip="1.2.3.4")

    print(f"Can create shifts: {permissions.can_create_shifts}")
    print(f"Can create checkouts: {permissions.can_create_checkouts}")


def example_get_xai_stats():
    """Example: Get XAI statistics."""
    client = SideShiftClient()

    # Get XAI coin statistics
    xai_stats = account.get_xai_stats(client)

    print(f"XAI Price (USD): ${xai_stats.xai_price_usd}")
    print(f"XAI Supply: {xai_stats.xai_supply}")


def example_get_coin_icon():
    """Example: Get coin icon."""
    client = SideShiftClient()

    # Get coin icon as SVG
    icon_svg = coins.get_coin_icon(client, coin_network="btc", format="svg")

    # Get coin icon as PNG
    icon_png = coins.get_coin_icon(client, coin_network="eth", format="png")

    # Save icon to file
    with open("btc-icon.svg", "wb") as f:
        f.write(icon_svg)

    with open("eth-icon.png", "wb") as f:
        f.write(icon_png)

    print("Icons saved successfully")


def example_get_checkout():
    """Example: Get checkout information."""
    client = SideShiftClient()

    # Get checkout information (no auth required)
    checkout_info = checkout.get_checkout(client, checkout_id="your-checkout-id")

    print(f"Checkout ID: {checkout_info.id}")
    print(f"Settle Coin: {checkout_info.settle_coin}")
    print(f"Settle Amount: {checkout_info.settle_amount}")


def example_create_checkout():
    """Example: Create a checkout."""
    client = SideShiftClient(
        secret="your-secret-key",
        affiliate_id="your-affiliate-id",
        user_ip="1.2.3.4",
    )

    # Create a checkout
    checkout_info = checkout.create_checkout(
        client,
        settle_coin="eth",
        settle_network="mainnet",
        settle_amount="1.0",
        settle_address="0x...",
        affiliate_id="your-affiliate-id",
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
        settle_memo="optional-memo",  # Required for some coins
    )

    print(f"Checkout created: {checkout_info.id}")
    print(f"Checkout URL: {checkout_info.checkout_url}")


if __name__ == "__main__":
    # Uncomment the example you want to run:
    # example_get_coins()
    # example_get_pair()
    # example_fixed_shift()
    # example_variable_shift()
    # example_get_account()
    # example_get_pairs()
    # example_get_shift()
    # example_get_bulk_shifts()
    # example_get_recent_shifts()
    # example_set_refund_address()
    # example_cancel_order()
    # example_get_permissions()
    # example_get_xai_stats()
    # example_get_coin_icon()
    # example_get_checkout()
    # example_create_checkout()
    pass

