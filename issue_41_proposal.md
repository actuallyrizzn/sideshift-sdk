## Proposed Solution for Issue #41: No Request ID/Correlation Tracking

**Problem:**
The SDK currently doesn't generate or track request IDs/correlation IDs, making it difficult to:
- Debug issues by correlating client requests with server logs
- Track requests across distributed systems
- Provide support with specific request identifiers

**Proposed Solution:**
1. Generate a unique request ID (UUID) for each HTTP request
2. Add `X-Request-ID` header to all requests (standard header name)
3. Extract `X-Request-ID` from response headers if present (API may echo it back)
4. Include request ID in log messages when logging is enabled
5. Store request ID in exception context for error tracking
6. Allow users to provide their own request ID via the `headers` parameter (takes precedence)

**Implementation Details:**
- Use Python's `uuid` module to generate UUID4 request IDs
- Add request ID generation in `_request` methods before making the HTTP call
- Include request ID in `_get_headers` or add it directly in `_request` methods
- Update logging statements to include request ID
- Add request ID to exception response_data when available
- Add constant for `X-Request-ID` header name

**Testing:**
- Test that request IDs are generated and included in headers
- Test that user-provided request IDs take precedence
- Test that request IDs appear in logs when logging is enabled
- Test that request IDs are extracted from response headers if present

