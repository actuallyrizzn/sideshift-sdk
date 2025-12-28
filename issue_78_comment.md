# Issue #78: [3.23] Missing Retry-After Header Parsing

## Solution

Enhanced Retry-After header parsing to support both integer (seconds) and HTTP-date formats (RFC 7231), and updated retry logic to use the Retry-After value when available instead of always using exponential backoff.

### Changes Made

1. **Enhanced `_handle_response` method:**
   - Improved Retry-After header parsing to support both integer (seconds) and HTTP-date formats
   - Added case-insensitive header lookup (`Retry-After` or `retry-after`)
   - Added HTTP-date parsing using `email.utils.parsedate_to_datetime` for RFC 7231 compliance
   - Stores parsed `retry_after` value in the exception's `response_data`

2. **Updated retry logic in `SideShiftClient._request`:**
   - Modified to extract `retry_after` from `SideShiftRateLimitError.response_data`
   - Uses Retry-After value for wait time if available and valid
   - Falls back to exponential backoff if Retry-After is not available or invalid
   - Added logging to indicate which delay method is being used

3. **Updated retry logic in `AsyncSideShiftClient._request`:**
   - Applied the same Retry-After parsing and usage logic for consistency

4. **Added comprehensive tests:**
   - Test that Retry-After header is correctly parsed (integer format)
   - Test that Retry-After value is used for retry delay instead of exponential backoff

### Benefits

- Respects server-specified retry delays via Retry-After header
- More efficient retry behavior (no unnecessary waiting)
- Supports both integer and HTTP-date formats per RFC 7231
- Maintains backward compatibility (falls back to exponential backoff if Retry-After is missing)
- Consistent behavior across sync and async clients

### Usage

The Retry-After header is automatically parsed and used. No code changes required:

```python
# If API returns 429 with Retry-After: 5, the SDK will wait 5 seconds before retrying
# If Retry-After is not present, exponential backoff is used
client = SideShiftClient(secret="...")
try:
    response = client.get("/endpoint")
except SideShiftRateLimitError as e:
    retry_after = e.response_data.get("retry_after")  # Can access the parsed value
```

All existing tests pass, and new tests verify the Retry-After parsing and usage.


