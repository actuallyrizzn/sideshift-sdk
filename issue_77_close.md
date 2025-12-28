# Issue #77: [3.22] No Request Timeout Configuration - RESOLVED

## Summary

Added per-request timeout configuration to all request methods, allowing users to override the client-level timeout on a per-request basis.

## Changes Made

1. **Added `timeout` parameter to `SideShiftClient` methods:**
   - `get()`: Added optional `timeout` parameter
   - `post()`: Added optional `timeout` parameter
   - `get_binary()`: Added optional `timeout` parameter
   - `_request()`: Added optional `timeout` parameter

2. **Added `timeout` parameter to `AsyncSideShiftClient` methods:**
   - `get()`: Added optional `timeout` parameter
   - `post()`: Added optional `timeout` parameter
   - `get_binary()`: Added optional `timeout` parameter
   - `_request()`: Added optional `timeout` parameter

3. **Timeout precedence logic:**
   - If `timeout` is provided to a request method, it overrides the client-level timeout
   - If `timeout` is `None`, the client-level timeout is used
   - This allows fine-grained control over timeout behavior per request

## Benefits

- Per-request timeout control for different endpoints or use cases
- Maintains backward compatibility (timeout parameter is optional)
- Consistent behavior across sync and async clients
- Allows longer timeouts for slow endpoints and shorter timeouts for fast endpoints

## Usage Example

```python
# Use client-level timeout (30 seconds default)
client = SideShiftClient(secret="...", timeout=30)
response = client.get("/coins")  # Uses 30 second timeout

# Override timeout for a specific request
response = client.get("/coins", timeout=60)  # Uses 60 second timeout
response = client.get("/coins", timeout=5)   # Uses 5 second timeout
```

All existing tests pass, confirming backward compatibility.

## Ada's Response

> Acknowledged. Issue #77 is resolved:
> - Per-request timeout parameters have been added to all request methods (get, post, get_binary, _request) in both sync and async clients.
> - Users may now override the client-level timeout for individual requests; if not specified, the default client timeout applies.
> - All tests pass, confirming backward compatibility and correct behavior.
> No further action is required for this fix unless additional timeout configuration or propagation issues arise. Continue with remaining issues and report if regressions or new requirements are identified.

## Commit

Commit ID: `13b2ed5`

