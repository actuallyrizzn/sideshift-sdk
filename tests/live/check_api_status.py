#!/usr/bin/env python3
"""Quick diagnostic to check API key status."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sideshift_sdk import SideShiftClient
from sideshift_sdk.endpoints import account

ACCOUNT_ID = os.getenv("SIDESHIFT_ACCOUNT_ID")
API_SECRET = os.getenv("SIDESHIFT_API_SECRET")

if not ACCOUNT_ID or not API_SECRET:
    print("ERROR: Missing credentials")
    sys.exit(1)

client = SideShiftClient(secret=API_SECRET, affiliate_id=ACCOUNT_ID)

print("=" * 60)
print("API KEY DIAGNOSTIC")
print("=" * 60)
print(f"Account ID: {ACCOUNT_ID}")
print(f"API Secret: {API_SECRET[:10]}...")
print()

print("=== 1. ACCOUNT ENDPOINT (GET /api/v2/account) ===")
try:
    acc = account.get_account(client)
    print(f"[OK] Status: SUCCESS (200 OK)")
    print(f"    Account ID: {acc.id}")
    print(f"    Total Balance: {acc.total_balance}")
    print(f"    Available: {acc.available}")
    account_works = True
except Exception as e:
    print(f"[FAIL] Status: FAILED")
    print(f"    Error: {e}")
    account_works = False

print()
print("=== 2. PERMISSIONS ENDPOINT (GET /api/v2/permissions) ===")
try:
    perms = account.get_permissions(client)
    print(f"[OK] Status: SUCCESS (200 OK)")
    print(f"    createShift: {perms.create_shift}")
    permissions_works = True
    has_shift_permission = perms.create_shift
except Exception as e:
    print(f"[FAIL] Status: FAILED")
    print(f"    Error: {e}")
    permissions_works = False
    has_shift_permission = False

print()
print("=" * 60)
print("DIAGNOSIS")
print("=" * 60)

if not account_works:
    print("[FAIL] API key is NOT recognized by SideShift API")
    print("       -> The secret key is invalid or not a valid API key")
elif not permissions_works:
    print("[WARN] API key is recognized but permissions check failed")
    print("       -> Key works but may have permission issues")
elif not has_shift_permission:
    print("[WARN] API key is VALID but createShift=False")
    print("       -> Key works, account exists, but lacks shift creation permission")
    print("       -> This explains 403 on /quotes and /shifts/variable")
else:
    print("[OK] API key is VALID with full permissions")
    print("     -> Key should work for quotes and shifts")
