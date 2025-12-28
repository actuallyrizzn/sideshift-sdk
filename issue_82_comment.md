# Issue #82: [3.27] Missing Compression Support

## Proposed Solution

Currently, the SDK doesn't explicitly request or handle HTTP compression (gzip, deflate). While some HTTP libraries handle this automatically, it's best practice to explicitly request compression via Accept-Encoding header.

**Solution:**
1. Add `Accept-Encoding: gzip, deflate` header to all requests
2. The underlying HTTP libraries (requests, httpx) will automatically decompress responses
3. This reduces bandwidth usage and improves performance
4. Make it configurable (enabled by default)

**Benefits:**
- Reduced bandwidth usage
- Faster response times
- Better performance for large responses
- Standard HTTP best practice

**Implementation:**
- Add Accept-Encoding header in `_get_headers` method
- Default to "gzip, deflate" (most common compression methods)
- Allow disabling compression if needed (for edge cases)

