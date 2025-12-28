## Issue Analysis: No Request Deduplication

**Problem**: When the same request (same method, endpoint, params, body) is made multiple times concurrently or within a short time window, the SDK makes duplicate HTTP calls. This wastes API rate limits and network resources.

**Use Cases**:
- Multiple parts of code requesting the same data simultaneously
- Retry logic triggering duplicate requests
- Concurrent requests in async scenarios

**Proposed Solution**:

I'll implement request deduplication that:
1. **Creates a request key** from method, endpoint, params, and body hash
2. **Tracks in-flight requests** - if the same request is already in progress, return the same future/promise
3. **Optional response caching** - cache successful responses for a short TTL (configurable, default disabled)
4. **Works for both sync and async** - sync uses threading, async uses asyncio

**Implementation Details**:
- Add `enable_request_deduplication` parameter to client constructors (default: False for backward compatibility)
- Add `request_cache_ttl` parameter for response caching (default: 0 = disabled)
- Use a dictionary to track in-flight requests by request key
- For sync: use threading locks to coordinate
- For async: use asyncio locks and futures
- Clean up completed requests from tracking dict

**Benefits**:
- Reduces duplicate API calls
- Saves rate limit quota
- Improves performance for concurrent duplicate requests
- Backward compatible (opt-in feature)

