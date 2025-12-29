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
            affiliate_id=ACCOUNT_ID,
            limit=5
        )
        print(f"Retrieved {len(recent_shifts)} recent shifts:")
        for shift in recent_shifts[:5]:
            print(f"  - Shift ID: {shift.id}")
            print(f"    Status: {shift.status}")
            print(f"    Deposit: {shift.deposit_coin} -> Settle: {shift.settle_coin}")
            if hasattr(shift, 'created'):
                print(f"    Created: {shift.created}")
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
            affiliate_id=ACCOUNT_ID,
            limit=1
        )
        
        if not recent_shifts:
            print("⚠ No recent shifts found, skipping get_shift test")
            return None
        
        shift_id = recent_shifts[0].id
        print(f"Testing with shift ID: {shift_id}")
        
        shift = shifts.get_shift(
            client,
            shift_id=shift_id,
            affiliate_id=ACCOUNT_ID
        )
        print(f"Shift ID: {shift.id}")
        print(f"Status: {shift.status}")
        print(f"Deposit Coin: {shift.deposit_coin}")
        print(f"Settle Coin: {shift.settle_coin}")
        if hasattr(shift, 'deposit_address'):
            print(f"Deposit Address: {shift.deposit_address}")
        print("[OK] Shift retrieved successfully")
        return shift
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
            affiliate_id=ACCOUNT_ID,
            limit=3
        )
        
        if len(recent_shifts) < 2:
            print("⚠ Not enough recent shifts found, skipping bulk test")
            return None
        
        shift_ids = [shift.id for shift in recent_shifts[:3]]
        print(f"Testing with shift IDs: {shift_ids}")
        
        bulk_shifts = shifts.get_bulk_shifts(
            client,
            shift_ids=shift_ids,
            affiliate_id=ACCOUNT_ID
        )
        print(f"Retrieved {len(bulk_shifts)} shifts:")
        for shift in bulk_shifts:
            print(f"  - {shift.id}: {shift.status}")
        print("[OK] Bulk shifts retrieved successfully")
        return bulk_shifts
    except Exception as e:
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
