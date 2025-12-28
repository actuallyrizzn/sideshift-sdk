# Issue #80: [3.25] Missing Content-Type Validation

## Proposed Solution

Currently, the SDK doesn't validate that API responses have the expected Content-Type header (e.g., `application/json`). This can lead to issues if the API returns unexpected content types or if responses are misconfigured.

**Solution:**
1. Add Content-Type validation in `_handle_response` method
2. For successful responses (200, 201) that are expected to be JSON, validate that Content-Type is `application/json` (or `application/json; charset=utf-8`, etc.)
3. Allow flexibility for binary responses (which should use `get_binary` method)
4. Raise `SideShiftAPIError` with clear error message if Content-Type is unexpected
5. Make validation configurable (optional, enabled by default)

**Benefits:**
- Catch API misconfigurations early
- Prevent parsing errors from unexpected content types
- Better error messages for developers
- Consistent validation across sync and async clients

**Implementation:**
- Add `_validate_content_type` helper method in `BaseClient`
- Call it in `_handle_response` for successful JSON responses
- Support case-insensitive header matching
- Support Content-Type with charset (e.g., `application/json; charset=utf-8`)
- Log warnings for unexpected Content-Types but allow them if validation is not strict

