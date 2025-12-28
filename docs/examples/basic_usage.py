"""Basic usage examples for SideShift SDK."""

from sideshift_sdk import SideShiftClient
from sideshift_sdk.endpoints import account, coins, pairs, quotes, shifts


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


if __name__ == "__main__":
    # Uncomment the example you want to run:
    # example_get_coins()
    # example_get_pair()
    # example_fixed_shift()
    # example_variable_shift()
    # example_get_account()
    pass

