# Best Practices Guide

This guide outlines best practices for using the SideShift SDK effectively and securely.

## Security Best Practices

### 1. Never Commit Secrets

**❌ Bad**:
```python
# Never do this
client = SideShiftClient(secret="sk_live_abc123...")
```

**✅ Good**:
```python
# Use environment variables
import os
client = SideShiftClient(secret=os.getenv("SIDESHIFT_SECRET"))
```

### 2. Use Environment Variables

Store sensitive information in environment variables:

```bash
# .env file (add to .gitignore)
export SIDESHIFT_SECRET="your-secret-key"
export AFFILIATE_ID="your-affiliate-id"
```

```python
# In your code
from sideshift_sdk import SideShiftClient

client = SideShiftClient(
    secret=os.getenv("SIDESHIFT_SECRET"),
    affiliate_id=os.getenv("AFFILIATE_ID"),
)
```

### 3. Validate User Input

Always validate user inputs before making API calls:

```python
def create_shift_safely(client, quote_id: str, settle_address: str):
    # Validate inputs
    if not quote_id or not isinstance(quote_id, str):
        raise ValueError("quote_id must be a non-empty string")
    
    if not settle_address or not isinstance(settle_address, str):
        raise ValueError("settle_address must be a non-empty string")
    
    # Validate address format (basic check)
    if not settle_address.startswith("0x") and len(settle_address) < 20:
        raise ValueError("Invalid address format")
    
    return shifts.create_fixed_shift(client, quote_id=quote_id, settle_address=settle_address)
```

### 4. Handle Errors Securely

Don't expose sensitive information in error messages:

```python
# ❌ Bad: Exposes secret in error
try:
    client = SideShiftClient(secret=user_input)
except Exception as e:
    print(f"Error: {e}")  # May expose secret

# ✅ Good: Generic error message
try:
    client = SideShiftClient(secret=user_input)
except Exception:
    print("Failed to initialize client. Please check your credentials.")
    # Log detailed error server-side only
    logger.error(f"Client init failed: {e}", exc_info=True)
```

## Code Organization

### 1. Reuse Client Instances

**❌ Bad**: Creating new clients for each request
```python
def get_quote():
    client = SideShiftClient(secret="...")
    return quotes.request_quote(client, ...)

def create_shift():
    client = SideShiftClient(secret="...")  # New client each time
    return shifts.create_fixed_shift(client, ...)
```

**✅ Good**: Reuse a single client instance
```python
class ShiftService:
    def __init__(self):
        self.client = SideShiftClient(secret=os.getenv("SIDESHIFT_SECRET"))
    
    def get_quote(self):
        return quotes.request_quote(self.client, ...)
    
    def create_shift(self):
        return shifts.create_fixed_shift(self.client, ...)
```

### 2. Use Context Managers

Ensure proper resource cleanup:

```python
# ✅ Good: Automatic cleanup
with SideShiftClient(secret="...") as client:
    quote = quotes.request_quote(client, ...)
    shift = shifts.create_fixed_shift(client, quote_id=quote.id, ...)
# Client automatically closed

# ✅ Good: Async
async with AsyncSideShiftClient(secret="...") as client:
    quote = await quotes.request_quote_async(client, ...)
    shift = await shifts.create_fixed_shift_async(client, quote_id=quote.id, ...)
```

### 3. Organize by Functionality

Group related operations:

```python
class QuoteService:
    def __init__(self, client):
        self.client = client
    
    def get_quote(self, deposit_coin, settle_coin, amount):
        return quotes.request_quote(
            self.client,
            deposit_coin=deposit_coin,
            settle_coin=settle_coin,
            deposit_amount=amount,
        )
    
    def create_shift_from_quote(self, quote_id, settle_address):
        return shifts.create_fixed_shift(
            self.client,
            quote_id=quote_id,
            settle_address=settle_address,
        )
```

## Error Handling

### 1. Use Specific Exception Types

```python
# ✅ Good: Specific exception handling
try:
    shift = shifts.create_fixed_shift(client, ...)
except SideShiftAuthenticationError:
    # Handle auth error specifically
    pass
except SideShiftRateLimitError as e:
    # Handle rate limit with retry logic
    if e.response_data and "retry_after" in e.response_data:
        wait_and_retry(e.response_data["retry_after"])
except SideShiftAPIError as e:
    # Handle other API errors
    log_error(e.status_code, e.message)
```

### 2. Implement Retry Logic

For transient errors:

```python
import time
from sideshift_sdk.exceptions import SideShiftRateLimitError, SideShiftAPIError

def create_shift_with_retry(client, quote_id, settle_address, max_retries=3):
    for attempt in range(max_retries):
        try:
            return shifts.create_fixed_shift(client, quote_id=quote_id, settle_address=settle_address)
        except SideShiftRateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = e.response_data.get("retry_after", 60) if e.response_data else 60
                time.sleep(wait_time)
                continue
            raise
        except SideShiftAPIError as e:
            if e.status_code >= 500 and attempt < max_retries - 1:
                # Retry on server errors
                time.sleep(2 ** attempt)
                continue
            raise
    raise Exception("Max retries exceeded")
```

## Performance

### 1. Use Async for Concurrent Operations

```python
# ✅ Good: Concurrent requests
async with AsyncSideShiftClient(secret="...") as client:
    results = await asyncio.gather(
        coins.get_coins_async(client),
        account.get_account_async(client),
        pairs.get_pairs_async(client, pairs=["btc-mainnet", "eth-mainnet"]),
    )
```

### 2. Cache Frequently Accessed Data

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=128)
def get_cached_coins(client, cache_key):
    """Cache coins list."""
    return coins.get_coins(client)

# Use with timestamp-based cache key
cache_key = datetime.now().strftime("%Y%m%d%H%M")  # Cache for 1 minute
coins_list = get_cached_coins(client, cache_key)
```

### 3. Batch Operations When Possible

```python
# ✅ Good: Batch shift retrieval
shift_ids = ["id1", "id2", "id3"]
shifts_list = shifts.get_bulk_shifts(client, shift_ids=shift_ids)

# Instead of:
# shift1 = shifts.get_shift(client, "id1")
# shift2 = shifts.get_shift(client, "id2")
# shift3 = shifts.get_shift(client, "id3")
```

## Testing

### 1. Use Test Fixtures

```python
import pytest
from sideshift_sdk import SideShiftClient

@pytest.fixture
def client():
    return SideShiftClient(secret="test-secret", affiliate_id="test-id")

def test_request_quote(client):
    # Use fixture
    quote = quotes.request_quote(client, ...)
    assert quote.id is not None
```

### 2. Mock API Responses

```python
from unittest.mock import patch, Mock

@patch('sideshift_sdk.client.SideShiftClient._request')
def test_get_coins(mock_request):
    mock_request.return_value = [{"coin": "btc", "name": "Bitcoin"}]
    client = SideShiftClient()
    coins_list = coins.get_coins(client)
    assert len(coins_list) > 0
```

## Logging and Monitoring

### 1. Implement Request Logging

```python
class LoggingClient(SideShiftClient):
    def _request(self, method, endpoint, **kwargs):
        logger.info(f"Request: {method} {endpoint}")
        start_time = time.time()
        
        try:
            response = super()._request(method, endpoint, **kwargs)
            duration = time.time() - start_time
            logger.info(f"Response: {method} {endpoint} - {duration:.2f}s")
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error: {method} {endpoint} - {duration:.2f}s - {e}")
            raise
```

### 2. Monitor Rate Limits

```python
rate_limit_count = 0

def track_rate_limits(func):
    def wrapper(*args, **kwargs):
        global rate_limit_count
        try:
            return func(*args, **kwargs)
        except SideShiftRateLimitError:
            rate_limit_count += 1
            logger.warning(f"Rate limit hit {rate_limit_count} times")
            raise
    return wrapper

@track_rate_limits
def create_shift(client, ...):
    return shifts.create_fixed_shift(client, ...)
```

## Type Safety

### 1. Use Type Hints

```python
from sideshift_sdk.models import Quote, Shift
from sideshift_sdk import SideShiftClient

def process_quote(client: SideShiftClient, quote: Quote) -> Shift:
    """Process a quote and create a shift."""
    return shifts.create_fixed_shift(
        client,
        quote_id=quote.id,
        settle_address="0x...",
    )
```

### 2. Validate Response Types

```python
quote = quotes.request_quote(client, ...)
assert isinstance(quote, Quote)
assert quote.id is not None
```

## Documentation

### 1. Document Your Integration

```python
def create_shift_for_user(
    client: SideShiftClient,
    user_id: str,
    deposit_coin: str,
    settle_coin: str,
    amount: str,
) -> Shift:
    """Create a shift for a user.
    
    Args:
        client: SideShift client instance
        user_id: Internal user identifier
        deposit_coin: Coin to deposit
        settle_coin: Coin to receive
        amount: Deposit amount
    
    Returns:
        Created shift object
    
    Raises:
        SideShiftAPIError: If shift creation fails
    """
    # Implementation
    pass
```

## Summary Checklist

- ✅ Never commit secrets to version control
- ✅ Use environment variables for credentials
- ✅ Validate all user inputs
- ✅ Reuse client instances
- ✅ Use context managers for cleanup
- ✅ Handle errors specifically
- ✅ Implement retry logic for transient errors
- ✅ Use async client for concurrent operations
- ✅ Cache frequently accessed data
- ✅ Batch operations when possible
- ✅ Add logging and monitoring
- ✅ Use type hints
- ✅ Write tests
- ✅ Document your code

## Additional Resources

- [Security Policy](SECURITY.md)
- [Performance Considerations](docs/PERFORMANCE.md)
- [Error Handling Examples](docs/examples/error_handling.py)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

