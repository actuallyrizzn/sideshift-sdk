## Issue #70: Response Caching - Already Implemented

Response caching is already implemented as part of issue #69 (Request Deduplication).

**Implementation:**
- `request_cache_ttl` parameter in `AsyncSideShiftClient.__init__()`
- `_check_request_cache()` method checks for cached responses
- `_store_request_cache()` method stores responses with TTL
- Automatic cache expiration and cleanup

**Usage:**
```python
client = AsyncSideShiftClient(
    secret="...",
    enable_request_deduplication=True,
    request_cache_ttl=60.0  # Cache responses for 60 seconds
)
```

The caching works in conjunction with request deduplication to avoid duplicate API calls and reuse cached responses.

