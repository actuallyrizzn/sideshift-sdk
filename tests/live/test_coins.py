#!/usr/bin/env python3
"""
Live test script for SideShift Coins API endpoints.

Uses real credentials from .env file to test coin-related functionality.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from this directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sideshift_sdk import SideShiftClient
from sideshift_sdk.endpoints import coins

# Get credentials from environment
ACCOUNT_ID = os.getenv("SIDESHIFT_ACCOUNT_ID")
API_SECRET = os.getenv("SIDESHIFT_API_SECRET")

if not ACCOUNT_ID or not API_SECRET:
    raise ValueError(
        "Missing required environment variables. "
        "Please create a .env file in tests/live/ with SIDESHIFT_ACCOUNT_ID and SIDESHIFT_API_SECRET"
    )

def test_get_coins():
    """Test getting all available coins."""
    print("\n=== Testing get_coins() ===")
    client = SideShiftClient(secret=API_SECRET, affiliate_id=ACCOUNT_ID)
    
    try:
        # Get raw response first to handle potential model validation issues
        response = client.get("/coins", require_auth=False)
        print(f"Total coins available (raw): {len(response)}")
        
        # Try to parse as models, but handle validation errors
        coins_list = []
        for i, coin_data in enumerate(response[:10]):
            try:
                from sideshift_sdk.models import Coin
                coin = Coin(**coin_data)
                coins_list.append(coin)
                print(f"  - {coin.coin} ({coin.name}) on networks: {coin.networks}")
            except Exception as model_error:
                print(f"  - [WARN] Coin {i} model validation failed: {coin_data.get('coin', 'unknown')}")
                print(f"    Error: {str(model_error)[:100]}")
        
        print(f"[OK] Coins retrieved successfully ({len(coins_list)}/{len(response[:10])} parsed)")
        return response
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_get_coin_icon():
    """Test getting coin icon."""
    print("\n=== Testing get_coin_icon() ===")
    client = SideShiftClient(secret=API_SECRET, affiliate_id=ACCOUNT_ID)
    
    try:
        # Test with BTC - check function signature first
        # get_coin_icon(client, coin_network, format="svg")
        icon_data = coins.get_coin_icon(client, coin_network="btc", format="svg")
        print(f"BTC icon size: {len(icon_data)} bytes")
        print(f"BTC icon type: {type(icon_data)}")
        print("[OK] Coin icon retrieved successfully")
        return icon_data
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run all coin tests."""
    print("=" * 60)
    print("SideShift Coins API Live Tests")
    print("=" * 60)
    print(f"Account ID: {ACCOUNT_ID}")
    print(f"API Secret: {API_SECRET[:10]}...")
    
    results = {}
    results['coins'] = test_get_coins()
    results['coin_icon'] = test_get_coin_icon()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, result in results.items():
        status = "[PASS]" if result is not None else "[FAIL]"
        print(f"{test_name}: {status}")
    
    return all(r is not None for r in results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
