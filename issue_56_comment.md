## Problem Description

The SDK has inconsistent header handling that can lead to issues:

1. **User headers can override SDK headers**: When user-provided headers are merged via `request_headers.update(headers)`, they can override critical SDK-managed headers like `Content-Type`, `Accept`, `User-Agent`, and `X-Request-ID`. This can break functionality.

2. **Inconsistent merging logic**: Different endpoints handle headers differently:
   - Some create headers dicts and pass them
   - Some pass headers directly
   - The merging doesn't protect SDK headers

3. **Case sensitivity**: HTTP headers are case-insensitive, but the code doesn't handle this consistently.

4. **No protection for critical headers**: SDK should protect headers it manages to ensure consistent behavior.

## Proposed Solution

1. Create a standardized `_merge_headers` method that:
   - Protects SDK-managed headers (Content-Type, Accept, User-Agent, X-Request-ID) from being overridden
   - Allows user headers to override non-critical headers
   - Handles case-insensitive header matching for protected headers
   - Logs warnings when user tries to override protected headers

2. Update all header merging points to use this standardized method

3. Add comprehensive tests for header merging behavior

