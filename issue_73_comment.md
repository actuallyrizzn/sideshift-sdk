## Issue #73: Missing Request Batching - Solution

**Problem**: No way to efficiently batch multiple API requests together.

**Solution**: Add batch request methods that allow making multiple requests efficiently:
- `batch_get()` / `batch_get_async()` - Batch multiple GET requests
- `batch_post()` / `batch_post_async()` - Batch multiple POST requests
- Uses asyncio.gather for async (concurrent execution)
- For sync, provides helper to execute sequentially but efficiently

**Implementation**:
- Add batch methods to both sync and async clients
- Accept list of request specifications
- Return list of results in same order
- Handle errors per-request (don't fail entire batch)

