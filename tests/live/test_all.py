#!/usr/bin/env python3
"""
Comprehensive live test script for all SideShift API endpoints.

Uses real credentials from .env file to test all functionality.
"""
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from this directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sideshift_sdk import SideShiftClient, AsyncSideShiftClient
from sideshift_sdk.endpoints import account, coins, pairs, quotes, shifts

# Get credentials from environment
ACCOUNT_ID = os.getenv("SIDESHIFT_ACCOUNT_ID")
API_SECRET = os.getenv("SIDESHIFT_API_SECRET")

if not ACCOUNT_ID or not API_SECRET:
    raise ValueError(
        "Missing required environment variables. "
        "Please create a .env file in tests/live/ with SIDESHIFT_ACCOUNT_ID and SIDESHIFT_API_SECRET"
    )

def test_sync_client():
    """Test synchronous client."""
    print("\n" + "=" * 60)
    print("SYNCHRONOUS CLIENT TESTS")
    print("=" * 60)
    
    client = SideShiftClient(secret=API_SECRET, affiliate_id=ACCOUNT_ID)
    results = {}
    
    # Account tests
    print("\n--- Account Tests ---")
    try:
        account_info = account.get_account(client)
        print(f"[OK] Account: {account_info.id}")
        results['account'] = True
    except Exception as e:
        print(f"[ERROR] Account: {e}")
        results['account'] = False
    
    try:
        permissions = account.get_permissions(client)
        print(f"[OK] Permissions: {permissions}")
        results['permissions'] = True
    except Exception as e:
        print(f"[ERROR] Permissions: {e}")
        results['permissions'] = False
    
    # Coins tests
    print("\n--- Coins Tests ---")
    try:
        coins_list = coins.get_coins(client)
        print(f"[OK] Coins: {len(coins_list)} available")
        results['coins'] = True
    except Exception as e:
        print(f"[ERROR] Coins: {e}")
        results['coins'] = False
    
    # Pairs tests
    print("\n--- Pairs Tests ---")
    try:
        pair = pairs.get_pair(client, from_coin="btc", to_coin="eth", affiliate_id=ACCOUNT_ID)
        print(f"[OK] Pair BTC->ETH: rate={pair.rate}")
        results['pair'] = True
    except Exception as e:
        print(f"[ERROR] Pair: {e}")
        results['pair'] = False
    
    # Quotes tests
    print("\n--- Quotes Tests ---")
    try:
        quote = quotes.request_quote(
            client,
            deposit_coin="btc",
            settle_coin="eth",
            deposit_amount="0.01",
            deposit_network="bitcoin",
            settle_network="mainnet",
            affiliate_id=ACCOUNT_ID
        )
        print(f"[OK] Quote: {quote.id}, rate={quote.rate}")
        results['quote'] = True
    except Exception as e:
        print(f"[ERROR] Quote: {e}")
        results['quote'] = False
    
    # Shifts tests
    print("\n--- Shifts Tests ---")
    try:
        recent_shifts = shifts.get_recent_shifts(client, affiliate_id=ACCOUNT_ID, limit=3)
        print(f"[OK] Recent Shifts: {len(recent_shifts)} found")
        results['recent_shifts'] = True
    except Exception as e:
        print(f"[ERROR] Recent Shifts: {e}")
        results['recent_shifts'] = False
    
    return results

async def test_async_client():
    """Test asynchronous client."""
    print("\n" + "=" * 60)
    print("ASYNCHRONOUS CLIENT TESTS")
    print("=" * 60)
    
    async with AsyncSideShiftClient(secret=API_SECRET, affiliate_id=ACCOUNT_ID) as client:
        results = {}
        
        # Account tests
        print("\n--- Account Tests (Async) ---")
        try:
            account_info = await account.get_account_async(client)
            print(f"[OK] Account: {account_info.id}")
            results['account'] = True
        except Exception as e:
            print(f"[ERROR] Account: {e}")
            results['account'] = False
        
        # Coins tests
        print("\n--- Coins Tests (Async) ---")
        try:
            coins_list = await coins.get_coins_async(client)
            print(f"[OK] Coins: {len(coins_list)} available")
            results['coins'] = True
        except Exception as e:
            print(f"[ERROR] Coins: {e}")
            results['coins'] = False
        
        # Pairs tests
        print("\n--- Pairs Tests (Async) ---")
        try:
            pair = await pairs.get_pair_async(client, from_coin="btc", to_coin="eth", affiliate_id=ACCOUNT_ID)
            print(f"[OK] Pair BTC->ETH: rate={pair.rate}")
            results['pair'] = True
        except Exception as e:
            print(f"[ERROR] Pair: {e}")
            results['pair'] = False
        
        return results

def main():
    """Run all tests."""
    print("=" * 60)
    print("SideShift SDK Comprehensive Live Tests")
    print("=" * 60)
    print(f"Account ID: {ACCOUNT_ID}")
    print(f"API Secret: {API_SECRET[:10]}...")
    
    # Sync tests
    sync_results = test_sync_client()
    
    # Async tests
    async_results = asyncio.run(test_async_client())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    print("\nSynchronous:")
    sync_pass = sum(1 for v in sync_results.values() if v)
    sync_total = len(sync_results)
    print(f"  Passed: {sync_pass}/{sync_total}")
    for test, passed in sync_results.items():
        print(f"    {test}: {'[OK]' if passed else '[FAIL]'}")
    
    print("\nAsynchronous:")
    async_pass = sum(1 for v in async_results.values() if v)
    async_total = len(async_results)
    print(f"  Passed: {async_pass}/{async_total}")
    for test, passed in async_results.items():
        print(f"    {test}: {'[OK]' if passed else '[FAIL]'}")
    
    total_pass = sync_pass + async_pass
    total_tests = sync_total + async_total
    print(f"\nOverall: {total_pass}/{total_tests} tests passed")
    
    return total_pass == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
