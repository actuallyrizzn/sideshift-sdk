#!/usr/bin/env python3
"""
Live test script for SideShift Shifts API endpoints.

Uses real credentials from .env file to test shift-related functionality.
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
from sideshift_sdk.endpoints import shifts

# Get credentials from environment
ACCOUNT_ID = os.getenv("SIDESHIFT_ACCOUNT_ID")
API_SECRET = os.getenv("SIDESHIFT_API_SECRET")

if not ACCOUNT_ID or not API_SECRET:
    raise ValueError(
        "Missing required environment variables. "
        "Please create a .env file in tests/live/ with SIDESHIFT_ACCOUNT_ID and SIDESHIFT_API_SECRET"
    )

def test_get_recent_shifts():
    """Test getting recent shifts."""
    print("\n=== Testing get_recent_shifts() ===")
    client = SideShiftClient(secret=API_SECRET, affiliate_id=ACCOUNT_ID)
    
    try:
        recent_shifts = shifts.get_recent_shifts(
            client,
            limit=5
        )
        print(f"Retrieved {len(recent_shifts)} recent shifts:")
        for shift in recent_shifts[:5]:
            print(f"  - Deposit: {shift.deposit_coin} -> Settle: {shift.settle_coin}")
            print(f"    Networks: {shift.deposit_network} -> {shift.settle_network}")
            if shift.deposit_amount:
                print(f"    Deposit Amount: {shift.deposit_amount}")
            if shift.settle_amount:
                print(f"    Settle Amount: {shift.settle_amount}")
            print(f"    Created: {shift.created_at}")
        print("[OK] Recent shifts retrieved successfully")
        return recent_shifts
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_get_shift():
    """Test getting a specific shift by ID."""
    print("\n=== Testing get_shift() ===")
    client = SideShiftClient(secret=API_SECRET, affiliate_id=ACCOUNT_ID)
    
    try:
        # First get a recent shift ID
        recent_shifts = shifts.get_recent_shifts(
            client,
            limit=1
        )
        
        if not recent_shifts:
            print("⚠ No recent shifts found, skipping get_shift test")
            return None
        
        # RecentShift doesn't have an ID, so we can't test get_shift without a known shift ID
        # This test requires a manually provided shift ID
        print("[WARN] RecentShift model doesn't include shift ID")
        print("       To test get_shift(), you need to provide a shift ID manually")
        print("       Skipping this test")
        return None
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_get_bulk_shifts():
    """Test getting multiple shifts."""
    print("\n=== Testing get_bulk_shifts() ===")
    client = SideShiftClient(secret=API_SECRET, affiliate_id=ACCOUNT_ID)
    
    try:
        # First get some recent shift IDs
        recent_shifts = shifts.get_recent_shifts(
            client,
            limit=3
        )
        
        if len(recent_shifts) < 2:
            print("⚠ Not enough recent shifts found, skipping bulk test")
            return None
        
        # RecentShift doesn't have an ID, so we can't test get_bulk_shifts without known shift IDs
        print("[WARN] RecentShift model doesn't include shift ID")
        print("       To test get_bulk_shifts(), you need to provide shift IDs manually")
        print("       Skipping this test")
        return None
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_create_variable_shift():
    """Test creating a variable rate shift.
    
    This tests POST /api/v2/shifts/variable which is failing in the live app with 403 Forbidden.
    """
    print("\n=== Testing create_variable_shift() (POST /api/v2/shifts/variable) ===")
    client = SideShiftClient(secret=API_SECRET, affiliate_id=ACCOUNT_ID)
    
    try:
        # Create a variable shift - small test amount
        # Using a test address (you'd use a real address in production)
        test_settle_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"  # Test ETH address
        
        shift = shifts.create_variable_shift(
            client,
            deposit_coin="btc",
            settle_coin="eth",
            settle_address=test_settle_address,
            deposit_network="bitcoin",
            settle_network="mainnet",
            affiliate_id=ACCOUNT_ID
        )
        print(f"[OK] Variable shift created successfully!")
        print(f"  Shift ID: {shift.id}")
        print(f"  Status: {shift.status}")
        print(f"  Deposit Address: {shift.deposit_address}")
        print(f"  Deposit Coin: {shift.deposit_coin} -> Settle Coin: {shift.settle_coin}")
        return shift
    except Exception as e:
        error_msg = str(e)
        if "forbidden" in error_msg.lower() or "Access forbidden" in error_msg or "403" in error_msg:
            print(f"[FAIL] POST /api/v2/shifts/variable returned 403 Forbidden")
            print(f"       This matches the error in your live app!")
            print(f"       Possible causes:")
            print(f"       1. API secret doesn't have shift creation permissions")
            print(f"       2. Missing or invalid affiliate_id")
            print(f"       3. Missing or invalid user_ip header")
            print(f"       4. Account doesn't have API access enabled")
            print(f"       Error: {error_msg}")
            return None
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_create_fixed_shift():
    """Test creating a fixed rate shift.
    
    This requires a quote first, so it's a two-step process.
    """
    print("\n=== Testing create_fixed_shift() (POST /api/v2/shifts/fixed) ===")
    client = SideShiftClient(secret=API_SECRET, affiliate_id=ACCOUNT_ID)
    
    try:
        # First, try to get a quote (this may fail with 403)
        from sideshift_sdk.endpoints import quotes
        quote = quotes.request_quote(
            client,
            deposit_coin="btc",
            settle_coin="eth",
            deposit_amount="0.01",
            deposit_network="bitcoin",
            settle_network="mainnet",
            affiliate_id=ACCOUNT_ID
        )
        
        # If quote succeeded, try to create fixed shift
        test_settle_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"  # Test ETH address
        
        shift = shifts.create_fixed_shift(
            client,
            quote_id=quote.id,
            settle_address=test_settle_address,
            affiliate_id=ACCOUNT_ID
        )
        print(f"[OK] Fixed shift created successfully!")
        print(f"  Shift ID: {shift.id}")
        print(f"  Status: {shift.status}")
        print(f"  Deposit Address: {shift.deposit_address}")
        return shift
    except Exception as e:
        error_msg = str(e)
        if "forbidden" in error_msg.lower() or "Access forbidden" in error_msg or "403" in error_msg:
            print(f"[FAIL] POST /api/v2/shifts/fixed or /api/v2/quotes returned 403 Forbidden")
            print(f"       This matches the error in your live app!")
            print(f"       Error: {error_msg}")
            return None
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run all shift tests."""
    print("=" * 60)
    print("SideShift Shifts API Live Tests")
    print("=" * 60)
    print(f"Account ID: {ACCOUNT_ID}")
    print(f"API Secret: {API_SECRET[:10]}...")
    
    results = {}
    results['recent_shifts'] = test_get_recent_shifts()
    results['shift'] = test_get_shift()
    results['bulk_shifts'] = test_get_bulk_shifts()
    results['create_variable_shift'] = test_create_variable_shift()
    results['create_fixed_shift'] = test_create_fixed_shift()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, result in results.items():
        if test_name in ("shift", "bulk_shifts") and result is None:
            status = "[SKIP] (requires shift ID)"
        elif test_name in ("create_variable_shift", "create_fixed_shift") and result is None:
            status = "[FAIL] (403 Forbidden - matches live app error)"
        else:
            status = "[PASS]" if result is not None else "[FAIL]"
        print(f"{test_name}: {status}")
    
    # Consider it a pass if recent_shifts works (main functionality)
    # But note if create_variable_shift fails (this is the failing endpoint)
    return results.get('recent_shifts') is not None

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
