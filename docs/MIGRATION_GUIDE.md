# Migration Guide

This guide helps you migrate to the SideShift SDK or migrate between SDK versions.

## Table of Contents

1. [Migrating from Manual API Calls](#migrating-from-manual-api-calls)
2. [Migrating Between SDK Versions](#migrating-between-sdk-versions)
3. [Migrating from Sync to Async Client](#migrating-from-sync-to-async-client)
4. [Configuration Migration](#configuration-migration)
5. [Error Handling Migration](#error-handling-migration)
6. [Model and Type Migration](#model-and-type-migration)

## Migrating from Manual API Calls

If you're currently making direct HTTP requests to the SideShift API, this section will help you migrate to the SDK.

### Installation

First, install the SDK:

```bash
pip install sideshift-sdk
```

### Basic Request Migration

**Before: Manual HTTP requests**

```python
import requests

# Get coins
response = requests.get(
    "https://sideshift.ai/api/v2/coins",
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
)
coins_data = response.json()

# Request a quote
response = requests.post(
    "https://sideshift.ai/api/v2/quotes",
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-sideshift-secret": "your-secret",
    },
    json={
        "depositCoin": "btc",
        "settleCoin": "eth",
        "depositAmount": "0.1",
    }
)
quote_data = response.json()
```

**After: Using the SDK**

```python
from sideshift_sdk import SideShiftClient
from sideshift_sdk.endpoints import coins, quotes

# Initialize client
client = SideShiftClient(secret="your-secret")

# Get coins
coins_list = coins.get_coins(client)

# Request a quote
quote = quotes.request_quote(
    client,
    deposit_coin="btc",
    settle_coin="eth",
    deposit_amount="0.1",
)
```

### Authentication Migration

**Before: Manual headers**

```python
headers = {
    "x-sideshift-secret": "your-secret",
    "x-user-ip": "1.2.3.4",
}
```

**After: SDK client configuration**

```python
client = SideShiftClient(
    secret="your-secret",
    user_ip="1.2.3.4",
)
```

Or use environment variables:

```bash
export SIDESHIFT_SECRET="your-secret"
export SIDESHIFT_USER_IP="1.2.3.4"
```

```python
client = SideShiftClient()  # Automatically reads from environment
```

### Error Handling Migration

**Before: Manual status code checking**

```python
response = requests.get("https://sideshift.ai/api/v2/coins")
if response.status_code == 401:
    raise ValueError("Authentication failed")
elif response.status_code == 429:
    raise ValueError("Rate limited")
elif response.status_code != 200:
    raise ValueError(f"API error: {response.status_code}")
data = response.json()
```

**After: SDK exceptions**

```python
from sideshift_sdk.exceptions import (
    SideShiftAuthenticationError,
    SideShiftRateLimitError,
    SideShiftAPIError,
)

try:
    coins_list = coins.get_coins(client)
except SideShiftAuthenticationError:
    # Handle authentication error
    pass
except SideShiftRateLimitError:
    # Handle rate limit (SDK automatically retries)
    pass
except SideShiftAPIError as e:
    # Handle other API errors
    print(f"API error: {e.message} (Status: {e.status_code})")
```

### Rate Limiting Migration

**Before: Manual retry logic**

```python
import time

def make_request_with_retry(url, headers, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            if attempt < max_retries - 1:
                time.sleep(retry_after)
                continue
        return response
    raise ValueError("Max retries exceeded")
```

**After: SDK automatic retry**

```python
# SDK automatically handles rate limits with exponential backoff
# No manual retry logic needed!
coins_list = coins.get_coins(client)
```

## Migrating Between SDK Versions

### Version 0.1.0

This is the initial release. No migration needed if you're starting fresh.

**Key Features:**
- Synchronous and asynchronous clients
- Full API V2 coverage
- Automatic rate limit handling
- Pydantic models for type safety
- Comprehensive error handling

### Future Versions

When new SDK versions are released, breaking changes will be documented here with migration steps.

## Migrating from Sync to Async Client

If you want to take advantage of concurrent requests and better performance, migrate from the sync client to the async client.

### When to Use Async

Use the async client when:
- You need to make multiple requests concurrently
- You're building an async application (e.g., FastAPI, aiohttp)
- You want better performance for I/O-bound operations

### Basic Migration

**Before: Sync client**

```python
from sideshift_sdk import SideShiftClient
from sideshift_sdk.endpoints import coins, account, pairs

client = SideShiftClient(secret="your-secret")

# Sequential requests
coins_list = coins.get_coins(client)
account_info = account.get_account(client)
pairs_list = pairs.get_pairs(client, pairs=["btc", "eth"])
```

**After: Async client**

```python
import asyncio
from sideshift_sdk import AsyncSideShiftClient
from sideshift_sdk.endpoints import coins, account, pairs

async def main():
    async with AsyncSideShiftClient(secret="your-secret") as client:
        # Concurrent requests
        coins_list, account_info, pairs_list = await asyncio.gather(
            coins.get_coins_async(client),
            account.get_account_async(client),
            pairs.get_pairs_async(client, pairs=["btc", "eth"]),
        )

asyncio.run(main())
```

### Context Manager Migration

**Before: Manual close**

```python
client = SideShiftClient(secret="your-secret")
try:
    # Use client
    pass
finally:
    client.close()
```

**After: Context manager (both sync and async)**

```python
# Sync
with SideShiftClient(secret="your-secret") as client:
    # Use client
    pass

# Async
async with AsyncSideShiftClient(secret="your-secret") as client:
    # Use client
    pass
```

## Configuration Migration

### Environment Variables

The SDK supports configuration via environment variables. Migrate hard-coded values to environment variables:

**Before: Hard-coded configuration**

```python
client = SideShiftClient(
    secret="hard-coded-secret",
    base_url="https://sideshift.ai/api/v2",
    timeout=30,
)
```

**After: Environment variables**

```bash
export SIDESHIFT_SECRET="your-secret"
export SIDESHIFT_BASE_URL="https://sideshift.ai/api/v2"
export SIDESHIFT_TIMEOUT="30"
```

```python
client = SideShiftClient()  # Reads from environment
```

### API Version Configuration

**Before: Hard-coded base URL**

```python
client = SideShiftClient(
    secret="your-secret",
    base_url="https://sideshift.ai/api/v2",
)
```

**After: API version parameter**

```python
client = SideShiftClient(
    secret="your-secret",
    api_version="v2",  # SDK constructs URL automatically
)
```

Or via environment variable:

```bash
export SIDESHIFT_API_VERSION="v2"
```

## Error Handling Migration

### Exception Types

The SDK provides specific exception types for different error scenarios:

| HTTP Status | SDK Exception | When Raised |
|-------------|---------------|-------------|
| 400 | `SideShiftAPIError` | Bad request |
| 401 | `SideShiftAuthenticationError` | Authentication failed |
| 403 | `SideShiftForbiddenError` | Access forbidden |
| 404 | `SideShiftNotFoundError` | Resource not found |
| 429 | `SideShiftRateLimitError` | Rate limit exceeded |
| 500+ | `SideShiftAPIError` | Server error |
| Network errors | `SideShiftNetworkError` | Connection/timeout errors |
| Size limits | `SideShiftSizeLimitError` | Request/response too large |

### Error Context

All exceptions include helpful context:

```python
try:
    coins.get_coins(client)
except SideShiftAPIError as e:
    print(f"Error: {e.message}")
    print(f"Status: {e.status_code}")
    print(f"Request ID: {e.request_id}")
    print(f"Method: {e.method}")
    print(f"Endpoint: {e.endpoint}")
    print(f"Response data: {e.response_data}")
```

## Model and Type Migration

### Using Pydantic Models

The SDK uses Pydantic models for type safety and validation:

**Before: Manual dict access**

```python
response = requests.get("https://sideshift.ai/api/v2/coins")
coins_data = response.json()
for coin in coins_data:
    coin_name = coin["name"]  # No type checking
    coin_networks = coin["networks"]  # No validation
```

**After: Pydantic models**

```python
from sideshift_sdk.endpoints import coins

coins_list = coins.get_coins(client)
for coin in coins_list:
    coin_name = coin.name  # Type-safe, IDE autocomplete
    coin_networks = coin.networks  # Validated, type-checked
```

### Type Hints

The SDK provides full type hints for IDE support:

```python
from sideshift_sdk import SideShiftClient
from sideshift_sdk.endpoints import quotes
from sideshift_sdk.models import Quote

client = SideShiftClient(secret="your-secret")

# Type hints enable IDE autocomplete and type checking
quote: Quote = quotes.request_quote(
    client,
    deposit_coin="btc",
    settle_coin="eth",
    deposit_amount="0.1",
)

# IDE knows quote.rate is a string
rate = quote.rate
```

### Enum Usage

The SDK uses enums for type-safe values:

```python
from sideshift_sdk.models import ShiftStatus

# Before: String comparison
if shift.status == "waiting":
    pass

# After: Enum comparison (type-safe)
if shift.status == ShiftStatus.WAITING:
    pass
```

## Common Migration Patterns

### Pattern 1: Replacing requests.get/post

**Before:**

```python
response = requests.get(url, headers=headers, params=params)
data = response.json()
```

**After:**

```python
data = client.get(endpoint, params=params, headers=headers)
```

### Pattern 2: Handling Rate Limits

**Before:**

```python
response = requests.get(url)
if response.status_code == 429:
    time.sleep(60)
    response = requests.get(url)
```

**After:**

```python
# SDK automatically retries with exponential backoff
data = client.get(endpoint)
```

### Pattern 3: Error Handling

**Before:**

```python
response = requests.get(url)
if response.status_code != 200:
    error_data = response.json()
    raise ValueError(error_data.get("message", "Unknown error"))
```

**After:**

```python
try:
    data = client.get(endpoint)
except SideShiftAPIError as e:
    # e.message contains the error message
    # e.response_data contains full error data
    raise
```

## Troubleshooting Migration Issues

### Issue: Import Errors

**Problem:** `ImportError: cannot import name 'X' from 'sideshift_sdk'`

**Solution:** Check that you're using the correct import path:

```python
# Correct
from sideshift_sdk import SideShiftClient
from sideshift_sdk.endpoints import coins
from sideshift_sdk.exceptions import SideShiftAPIError

# Incorrect
from sideshift_sdk.coins import get_coins  # Wrong!
```

### Issue: Type Errors

**Problem:** Type checker complains about return types

**Solution:** Use type hints and Pydantic models:

```python
from sideshift_sdk.models import Coin

coins_list: list[Coin] = coins.get_coins(client)
```

### Issue: Configuration Not Working

**Problem:** Environment variables not being read

**Solution:** Ensure environment variables are set before importing:

```python
import os
os.environ["SIDESHIFT_SECRET"] = "your-secret"

from sideshift_sdk import SideShiftClient
client = SideShiftClient()  # Now reads from environment
```

## Next Steps

After migration:

1. **Review Best Practices**: See `docs/BEST_PRACTICES.md`
2. **Check Performance**: See `docs/PERFORMANCE.md`
3. **Understand Error Handling**: See `docs/ERROR_CODES.md`
4. **Learn About Rate Limits**: See `docs/RATE_LIMITS.md`

## Getting Help

If you encounter issues during migration:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review the [API Documentation](SIDESHIFT_API_DOCUMENTATION.md)
3. Open an issue on GitHub
4. Check existing issues for similar problems

