# Issue #79: [3.24] No Request Body Validation

## Proposed Solution

Currently, the SDK only validates request body size but doesn't validate that the request body is actually JSON-serializable before attempting to send it. This can lead to cryptic errors from the HTTP library.

**Solution:**
1. Add validation in `_request` methods to ensure `json_data` is a valid dictionary/JSON-serializable object
2. Attempt JSON serialization early to catch serialization errors before making the HTTP request
3. Provide clear error messages with context (method, endpoint, request_id)
4. Raise a `SideShiftAPIError` (or a new validation error) if the body is invalid

**Benefits:**
- Catch errors earlier (before network call)
- Better error messages for developers
- Prevent invalid requests from being sent
- Consistent validation across sync and async clients

**Implementation:**
- Add a `_validate_request_body` helper method in `BaseClient`
- Call it in both `SideShiftClient._request` and `AsyncSideShiftClient._request` before the retry loop
- Validate that `json_data` is either `None` or a JSON-serializable dict
- Attempt `json.dumps()` and catch serialization errors, raising a clear exception


