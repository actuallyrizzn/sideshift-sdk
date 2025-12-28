# Issue #81: [3.26] No Charset Handling

## Proposed Solution

Currently, the SDK doesn't explicitly handle charset in Content-Type headers. While UTF-8 is the default for JSON, it's best practice to explicitly specify charset in request headers and parse it from response headers.

**Solution:**
1. Add `charset=utf-8` to Content-Type header in requests (e.g., `application/json; charset=utf-8`)
2. Parse charset from response Content-Type headers
3. Use the parsed charset when decoding response content (if different from UTF-8)
4. Default to UTF-8 if charset is not specified
5. Add helper method to extract charset from Content-Type header

**Benefits:**
- Explicit charset specification improves compatibility
- Proper handling of non-UTF-8 responses (if API ever returns them)
- Better adherence to HTTP standards
- Consistent behavior across sync and async clients

**Implementation:**
- Update `_get_headers` to include `charset=utf-8` in Content-Type
- Add `_parse_charset_from_content_type` helper method
- Use parsed charset when decoding response content (if needed)
- Default to UTF-8 for all JSON operations

