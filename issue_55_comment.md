## Problem Description

The SDK currently has no limits on request or response body sizes. This can lead to:

1. **Memory Issues**: Large responses are loaded entirely into memory via `response.json()`, which can cause OOM errors
2. **No Request Validation**: Large request bodies can be sent without validation, potentially causing issues on the server side
3. **No Protection**: Malicious or accidental large payloads could exhaust system resources

## Proposed Solution

1. Add configurable `max_request_size` and `max_response_size` parameters (default: 10MB for requests, 50MB for responses)
2. Validate request body size before sending (check serialized JSON size)
3. Check response size before parsing:
   - Use `Content-Length` header if available
   - For streaming responses, check size incrementally
   - Raise `SideShiftSizeLimitError` if limit exceeded
4. Add configuration via `SDKConfig` and environment variables
5. Add appropriate exception type for size limit errors

