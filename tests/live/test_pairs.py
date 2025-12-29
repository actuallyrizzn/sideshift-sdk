#!/usr/bin/env python3
"""
Live test script for SideShift Pairs API endpoints.

Uses real credentials from .env file to test pair-related functionality.
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
from sideshift_sdk.endpoints import pairs

# Get credentials from environment
ACCOUNT_ID = os.getenv("SIDESHIFT_ACCOUNT_ID")
API_SECRET = os.getenv("SIDESHIFT_API_SECRET")

if not ACCOUNT_ID or not API_SECRET:
    raise ValueError(
        "Missing required environment variables. "
        "Please create a .env file in tests/live/ with SIDESHIFT_ACCOUNT_ID and SIDESHIFT_API_SECRET"
    )

def test_get_pair():
    """Test getting pair information."""
    print("\n=== Testing get_pair() ===")
    client = SideShiftClient(secret=API_SECRET, affiliate_id=ACCOUNT_ID)
    
    try:
        # Test BTC to ETH pair
        pair = pairs.get_pair(
            client,
            from_coin="btc",
            to_coin="eth",
            affiliate_id=ACCOUNT_ID
        )
        print(f"Pair: BTC -> ETH")
        print(f"  Rate: {pair.rate}")
        print(f"  Min: {pair.min}")
        print(f"  Max: {pair.max}")
        if hasattr(pair, 'rate_type'):
            print(f"  Rate Type: {pair.rate_type}")
        print("[OK] Pair info retrieved successfully")
        return pair
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_get_pairs():
    """Test getting multiple pairs information."""
    print("\n=== Testing get_pairs() ===")
    client = SideShiftClient(secret=API_SECRET, affiliate_id=ACCOUNT_ID)
    
    try:
        # Test multiple pairs
        pair_list = [
            {"from": "btc", "to": "eth"},
            {"from": "eth", "to": "btc"},
            {"from": "btc", "to": "usdt"},
        ]
        
        pairs_data = pairs.get_pairs(
            client,
            pair_list=pair_list,
            affiliate_id=ACCOUNT_ID
        )
        print(f"Retrieved {len(pairs_data)} pairs:")
        for pair in pairs_data:
            print(f"  - {pair.from_coin} -> {pair.to_coin}: rate={pair.rate}, min={pair.min}, max={pair.max}")
        print("[OK] Multiple pairs retrieved successfully")
        return pairs_data
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run all pair tests."""
    print("=" * 60)
    print("SideShift Pairs API Live Tests")
    print("=" * 60)
    print(f"Account ID: {ACCOUNT_ID}")
    print(f"API Secret: {API_SECRET[:10]}...")
    
    results = {}
    results['pair'] = test_get_pair()
    results['pairs'] = test_get_pairs()
    
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
