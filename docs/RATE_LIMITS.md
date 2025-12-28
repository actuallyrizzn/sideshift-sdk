# Rate Limit Documentation

Complete documentation on rate limits and how the SideShift SDK handles them.

## Rate Limits Overview

SideShift.ai enforces rate limits per IP address to ensure fair usage and API stability.

### Rate Limits by Endpoint

| Endpoint Category | Limit | Time Window |
|-------------------|-------|-------------|
| Creating Shifts  | 5     | Per minute  |
| Requesting Quotes| 20    | Per minute  |
| Other Endpoints  | Varies| Per minute  |

## Automatic Rate Limit Handling

The SDK automatically handles rate limits with exponential backoff retry logic.

### How It Works

1. **Request Made**: SDK makes an API request
2. **Rate Limit Detected**: If the API returns HTTP 429 (Too Many Requests)
3. **Retry-After Header**: SDK checks for `Retry-After` header
4. **Exponential Backoff**: Waits with exponential backoff (up to 3 retries by default)
5. **Retry**: Automatically retries the request
6. **Raise Exception**: If all retries fail, raises `SideShiftRateLimitError`

### Retry Configuration

Default retry behavior:
- **Max Retries**: 3 attempts
- **Base Delay**: 1 second
- **Max Delay**: 60 seconds
- **Backoff Formula**: `min(base_delay * (2^attempt), max_delay)`

### Customizing Retry Behavior

You can customize retry behavior by subclassing the client:

```python
class CustomClient(SideShiftClient):
    def _request(self, ..., max_retries=5):  # Increase retries
        return super()._request(..., max_retries=max_retries)
```

## Rate Limit Exceptions

### SideShiftRateLimitError

When rate limited, the SDK raises `SideShiftRateLimitError`:

```python
from sideshift_sdk.exceptions import SideShiftRateLimitError

try:
    shift = shifts.create_fixed_shift(client, ...)
except SideShiftRateLimitError as e:
    print(f"Rate limited: {e.message}")
    if e.response_data and "retry_after" in e.response_data:
        wait_time = e.response_data["retry_after"]
        print(f"Retry after {wait_time} seconds")
```

### Exception Attributes

- `message`: Error message
- `response_data`: Dictionary containing `retry_after` (if available)
- `status_code`: Always 429

## Best Practices

### 1. Implement Request Queuing

For high-volume applications, implement request queuing:

```python
import asyncio
from collections import deque

class RateLimitedClient:
    def __init__(self, client):
        self.client = client
        self.queue = deque()
        self.last_request_time = 0
        self.min_interval = 12  # 5 requests per minute = 12 seconds between requests
    
    async def create_shift(self, *args, **kwargs):
        # Wait if needed
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.min_interval:
            await asyncio.sleep(self.min_interval - time_since_last)
        
        result = await shifts.create_fixed_shift_async(self.client, *args, **kwargs)
        self.last_request_time = time.time()
        return result
```

### 2. Monitor Rate Limit Errors

Track rate limit errors to optimize request patterns:

```python
rate_limit_count = 0

try:
    result = quotes.request_quote(client, ...)
except SideShiftRateLimitError:
    rate_limit_count += 1
    # Log or alert
    print(f"Rate limit hit {rate_limit_count} times")
```

### 3. Use Async Client for Concurrent Operations

The async client allows concurrent requests while respecting rate limits:

```python
async with AsyncSideShiftClient(secret="...") as client:
    # These will be rate-limited automatically
    tasks = [
        quotes.request_quote_async(client, ...),
        quotes.request_quote_async(client, ...),
        quotes.request_quote_async(client, ...),
    ]
    results = await asyncio.gather(*tasks)
```

### 4. Cache Frequently Accessed Data

Cache data that doesn't change frequently:

```python
from functools import lru_cache
from datetime import datetime, timedelta

cache_expiry = {}
CACHE_TTL = timedelta(minutes=5)

@lru_cache(maxsize=128)
def get_cached_coins(client):
    """Cache coins list for 5 minutes."""
    return coins.get_coins(client)

# Use cached version
coins_list = get_cached_coins(client)
```

## Rate Limit Headers

The API may include rate limit information in response headers:

- `Retry-After`: Number of seconds to wait before retrying (when rate limited)
- `X-RateLimit-Limit`: Maximum requests allowed (if provided)
- `X-RateLimit-Remaining`: Remaining requests (if provided)
- `X-RateLimit-Reset`: Time when rate limit resets (if provided)

The SDK automatically uses the `Retry-After` header when available.

## Testing Rate Limits

To test rate limit handling:

1. Make rapid requests to trigger rate limits
2. Verify automatic retry behavior
3. Check that `SideShiftRateLimitError` is raised after max retries
4. Verify exponential backoff timing

## Troubleshooting Rate Limits

### Issue: Frequent Rate Limit Errors

**Solutions**:
- Reduce request frequency
- Implement request queuing
- Use caching for frequently accessed data
- Distribute requests across multiple IP addresses (if applicable)

### Issue: Rate Limits Not Being Handled

**Solutions**:
- Ensure you're using the latest SDK version
- Check that exceptions are being caught properly
- Verify network connectivity
- Check API status

## Rate Limit Examples

See `docs/examples/error_handling.py` for examples of handling rate limit errors.

## Additional Resources

- [SideShift.ai API Documentation](docs/SIDESHIFT_API_DOCUMENTATION.md)
- [Performance Considerations](docs/PERFORMANCE.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

