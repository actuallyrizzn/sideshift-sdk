## Issue Analysis: Duplicate Code Between Sync and Async

After investigating the codebase, I've identified significant code duplication between the synchronous (`SideShiftClient`) and asynchronous (`AsyncSideShiftClient`) implementations:

### Areas of Duplication:

1. **Client `_request` methods** (~200 lines each):
   - Request ID generation
   - Header merging
   - Request body validation
   - Request size validation
   - Retry logic with exponential backoff
   - Response handling
   - Error handling and hook execution
   - The only differences are:
     - Sync uses `requests.Session` and `time.sleep()`
     - Async uses `httpx.AsyncClient` and `await asyncio.sleep()`
     - Async hooks need to handle both sync and async hooks

2. **Endpoint functions** (across all endpoint modules):
   - Each endpoint has both `function_name()` and `function_name_async()` versions
   - Logic is nearly identical except for `await` keywords
   - Some async versions have additional validation (inconsistency)

3. **`get_binary` methods**:
   - Nearly identical implementations in both clients

### Proposed Solution:

I'll implement a refactoring strategy to reduce duplication:

1. **Extract common request logic to BaseClient**:
   - Create a shared `_prepare_request()` method for common setup (headers, validation, etc.)
   - Create a shared `_execute_request()` abstract method that each client implements
   - Move retry logic to a shared helper that works with both sync/async

2. **Use a unified endpoint pattern**:
   - Create a decorator or helper that can generate both sync and async versions
   - Or refactor endpoints to accept a generic client interface

3. **Share binary request logic**:
   - Move `get_binary` implementation to BaseClient with abstract HTTP client access

This refactoring will:
- Reduce code duplication by ~40-50%
- Make maintenance easier (fix bugs once)
- Ensure sync and async behavior stays consistent
- Preserve backward compatibility

I'll start with the client-level refactoring first, then address endpoint duplication if time permits.

