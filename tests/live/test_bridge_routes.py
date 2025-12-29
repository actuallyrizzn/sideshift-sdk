#!/usr/bin/env python3
"""
Test bridge routes and get fee/slippage information for SOL->BASE and TON->BASE.

Uses real credentials from .env file.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load .env file from this directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sideshift_sdk import SideShiftClient
from sideshift_sdk.endpoints import pairs, quotes, coins

# Get credentials from environment
ACCOUNT_ID = os.getenv("SIDESHIFT_ACCOUNT_ID")
API_SECRET = os.getenv("SIDESHIFT_API_SECRET")

if not ACCOUNT_ID or not API_SECRET:
    raise ValueError(
        "Missing required environment variables. "
        "Please create a .env file in tests/live/ with SIDESHIFT_ACCOUNT_ID and SIDESHIFT_API_SECRET"
    )

def get_eth_price_usd():
    """Get current ETH price in USD from CoinGecko."""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("ethereum", {}).get("usd", None)
    except Exception as e:
        print(f"[WARN] Could not fetch ETH price: {e}")
    return None

def get_sol_price_usd():
    """Get current SOL price in USD from CoinGecko."""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("solana", {}).get("usd", None)
    except Exception as e:
        print(f"[WARN] Could not fetch SOL price: {e}")
    return None

def get_ton_price_usd():
    """Get current TON price in USD from CoinGecko."""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("the-open-network", {}).get("usd", None)
    except Exception as e:
        print(f"[WARN] Could not fetch TON price: {e}")
    return None

def get_coin_networks(client, coin_symbol):
    """Get available networks for a coin."""
    try:
        coins_list = coins.get_coins(client)
        for coin in coins_list:
            if coin.coin.lower() == coin_symbol.lower():
                return coin.networks
        return []
    except Exception as e:
        print(f"[ERROR] Error getting networks for {coin_symbol}: {e}")
        return []

def check_route(client, from_coin, to_coin, from_network=None, to_network=None, eth_price=None, sol_price=None, ton_price=None):
    """Check if a route exists and get pair information."""
    print(f"\n{'='*60}")
    print(f"Checking route: {from_coin.upper()} -> {to_coin.upper()}")
    if from_network:
        print(f"  From network: {from_network}")
    if to_network:
        print(f"  To network: {to_network}")
    print(f"{'='*60}")
    
    # Format: coin-network (e.g., "sol-solana", "eth-base")
    from_pair = f"{from_coin}-{from_network}" if from_network else from_coin
    to_pair = f"{to_coin}-{to_network}" if to_network else to_coin
    
    try:
        # Get pair information
        pair = pairs.get_pair(
            client,
            from_coin=from_pair,
            to_coin=to_pair,
            affiliate_id=ACCOUNT_ID
        )
        
        print(f"[OK] Route exists!")
        rate_float = float(pair.rate)
        min_float = float(pair.min)
        max_float = float(pair.max)
        
        print(f"  Rate: {pair.rate}")
        print(f"  Min deposit: {pair.min} {from_coin.upper()}", end="")
        if from_coin.lower() == "sol" and sol_price:
            min_usd = min_float * sol_price
            print(f" (~${min_usd:,.2f} USD)")
        elif from_coin.lower() == "ton" and ton_price:
            min_usd = min_float * ton_price
            print(f" (~${min_usd:,.2f} USD)")
        else:
            print()
        
        print(f"  Max deposit: {pair.max} {from_coin.upper()}", end="")
        if from_coin.lower() == "sol" and sol_price:
            max_usd = max_float * sol_price
            print(f" (~${max_usd:,.2f} USD)")
        elif from_coin.lower() == "ton" and ton_price:
            max_usd = max_float * ton_price
            print(f" (~${max_usd:,.2f} USD)")
        else:
            print()
        
        print(f"  Deposit network: {pair.deposit_network}")
        print(f"  Settle network: {pair.settle_network}")
        
        # Calculate fee estimate based on rate
        # The rate represents how much ETH you get per 1 unit of source coin
        rate_float = float(pair.rate)
        
        print(f"\n  Fee/Slippage Estimate (based on pair rate):")
        print(f"    Exchange rate: 1 {from_coin.upper()} = {rate_float} ETH")
        if eth_price:
            eth_value = rate_float * eth_price
            print(f"    USD value: 1 {from_coin.upper()} = ${eth_value:.2f} USD (via ETH)")
        
        # Example calculations
        for test_amount in ["0.1", "1.0", "10.0"]:
            try:
                amount_float = float(test_amount)
                expected_eth = amount_float * rate_float
                eth_usd = expected_eth * eth_price if eth_price else None
                if eth_usd:
                    print(f"    {test_amount} {from_coin.upper()} -> ~{expected_eth:.8f} ETH (~${eth_usd:.2f} USD)")
                else:
                    print(f"    {test_amount} {from_coin.upper()} -> ~{expected_eth:.8f} ETH")
            except:
                pass
        
        return pair
    except Exception as e:
        print(f"[ERROR] Route check failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_quote_info(client, from_coin, to_coin, from_network, to_network, amount="0.1", eth_price=None, sol_price=None, ton_price=None):
    """Get quote information including fees and slippage."""
    print(f"\n{'='*60}")
    print(f"Getting quote: {amount} {from_coin.upper()} -> {to_coin.upper()}")
    print(f"  From network: {from_network}")
    print(f"  To network: {to_network}")
    print(f"{'='*60}")
    
    try:
        quote = quotes.request_quote(
            client,
            deposit_coin=from_coin,
            settle_coin=to_coin,
            deposit_amount=amount,
            deposit_network=from_network,
            settle_network=to_network,
            affiliate_id=ACCOUNT_ID
        )
        
        print(f"[OK] Quote received!")
        print(f"  Quote ID: {quote.id}")
        print(f"  Deposit amount: {quote.deposit_amount} {from_coin.upper()}")
        print(f"  Settle amount: {quote.settle_amount} {to_coin.upper()}")
        print(f"  Rate: {quote.rate}")
        
        # Calculate fees/slippage
        deposit_float = float(quote.deposit_amount)
        settle_float = float(quote.settle_amount)
        rate_float = float(quote.rate)
        
        # Calculate effective rate
        effective_rate = settle_float / deposit_float
        print(f"\n  Fee/Slippage Analysis:")
        print(f"    Effective rate: {effective_rate}")
        print(f"    Quoted rate: {rate_float}")
        
        # Calculate percentage difference (slippage/fee)
        if rate_float > 0:
            slippage_pct = ((effective_rate - rate_float) / rate_float) * 100
            print(f"    Slippage/Fee: {slippage_pct:.4f}%")
        
        # Calculate fee amount
        expected_settle = deposit_float * rate_float
        fee_amount = expected_settle - settle_float
        if fee_amount > 0:
            print(f"    Estimated fee: {fee_amount:.8f} {to_coin.upper()}")
        else:
            print(f"    Estimated fee: {abs(fee_amount):.8f} {to_coin.upper()} (bonus)")
        
        if hasattr(quote, 'expires_at'):
            print(f"  Expires at: {quote.expires_at}")
        
        return quote
    except Exception as e:
        error_msg = str(e)
        if "forbidden" in error_msg.lower() or "Access forbidden" in error_msg:
            print(f"[WARN] Quote requires user_ip header (not available in this test)")
            print(f"       Using pair rate for fee estimation instead")
            # Calculate based on pair rate
            try:
                pair = pairs.get_pair(
                    client,
                    from_coin=f"{from_coin}-{from_network}" if from_network else from_coin,
                    to_coin=f"{to_coin}-{to_network}" if to_network else to_coin,
                    affiliate_id=ACCOUNT_ID
                )
                rate_float = float(pair.rate)
                amount_float = float(amount)
                expected_eth = amount_float * rate_float
                eth_usd = expected_eth * eth_price if eth_price else None
                source_usd = amount_float * (sol_price if from_coin.lower() == "sol" else ton_price) if (from_coin.lower() == "sol" and sol_price) or (from_coin.lower() == "ton" and ton_price) else None
                
                print(f"       Estimated: {amount} {from_coin.upper()}", end="")
                if source_usd:
                    print(f" (${source_usd:,.2f} USD)", end="")
                print(f" -> ~{expected_eth:.8f} ETH", end="")
                if eth_usd:
                    print(f" (${eth_usd:,.2f} USD)")
                else:
                    print()
                print(f"       Rate: {rate_float}")
                return {"rate": rate_float, "estimated_settle": expected_eth, "source": "pair_rate"}
            except:
                pass
        else:
            print(f"[ERROR] Quote request failed: {e}")
            import traceback
            traceback.print_exc()
        return None

def main():
    """Test bridge routes."""
    print("=" * 60)
    print("Bridge Route Testing: SOL->BASE and TON->BASE")
    print("=" * 60)
    print(f"Account ID: {ACCOUNT_ID}")
    print(f"API Secret: {API_SECRET[:10]}...")
    
    # Get current prices
    print("\nFetching current prices...")
    eth_price = get_eth_price_usd()
    sol_price = get_sol_price_usd()
    ton_price = get_ton_price_usd()
    
    if eth_price:
        print(f"  ETH: ${eth_price:,.2f} USD")
    if sol_price:
        print(f"  SOL: ${sol_price:,.2f} USD")
    if ton_price:
        print(f"  TON: ${ton_price:,.2f} USD")
    
    client = SideShiftClient(secret=API_SECRET, affiliate_id=ACCOUNT_ID)
    
    # Test SOL -> BASE (ETH)
    print("\n" + "="*60)
    print("TEST 1: SOL -> BASE (ETH)")
    print("="*60)
    
    # Get available networks for SOL
    sol_networks = get_coin_networks(client, "sol")
    print(f"SOL available networks: {sol_networks}")
    
    # Check route
    sol_pair = check_route(
        client,
        from_coin="sol",
        to_coin="eth",
        from_network="solana",
        to_network="base",
        eth_price=eth_price,
        sol_price=sol_price,
        ton_price=ton_price
    )
    
    if sol_pair:
        # Get quote with different amounts
        print("\n--- Testing with 0.1 SOL ---")
        quote1 = get_quote_info(
            client,
            from_coin="sol",
            to_coin="eth",
            from_network="solana",
            to_network="base",
            amount="0.1",
            eth_price=eth_price,
            sol_price=sol_price,
            ton_price=ton_price
        )
        
        print("\n--- Testing with 1.0 SOL ---")
        quote2 = get_quote_info(
            client,
            from_coin="sol",
            to_coin="eth",
            from_network="solana",
            to_network="base",
            amount="1.0",
            eth_price=eth_price,
            sol_price=sol_price,
            ton_price=ton_price
        )
    
    # Test TON -> BASE (ETH)
    print("\n" + "="*60)
    print("TEST 2: TON -> BASE (ETH)")
    print("="*60)
    
    # Get available networks for TON
    ton_networks = get_coin_networks(client, "ton")
    print(f"TON available networks: {ton_networks}")
    
    # Check route
    ton_pair = check_route(
        client,
        from_coin="ton",
        to_coin="eth",
        from_network="ton" if "ton" in ton_networks else None,
        to_network="base",
        eth_price=eth_price,
        sol_price=sol_price,
        ton_price=ton_price
    )
    
    if ton_pair:
        # Get quote with different amounts
        print("\n--- Testing with 0.1 TON ---")
        quote3 = get_quote_info(
            client,
            from_coin="ton",
            to_coin="eth",
            from_network="ton" if "ton" in ton_networks else None,
            to_network="base",
            amount="0.1",
            eth_price=eth_price,
            sol_price=sol_price,
            ton_price=ton_price
        )
        
        print("\n--- Testing with 1.0 TON ---")
        quote4 = get_quote_info(
            client,
            from_coin="ton",
            to_coin="eth",
            from_network="ton" if "ton" in ton_networks else None,
            to_network="base",
            amount="1.0",
            eth_price=eth_price,
            sol_price=sol_price,
            ton_price=ton_price
        )
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"SOL -> BASE route: {'[OK]' if sol_pair else '[FAIL]'}")
    print(f"TON -> BASE route: {'[OK]' if ton_pair else '[FAIL]'}")
    
    return sol_pair is not None and ton_pair is not None

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
