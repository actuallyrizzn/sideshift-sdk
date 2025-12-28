# Issue #67: [3.12] Incomplete Type Coverage

## Solution

Added type annotations to all class attributes in `BaseClient`, `SideShiftClient`, and `AsyncSideShiftClient` to improve type coverage and enable better static type checking.

### Changes Made

1. **BaseClient class attributes:**
   - Added type annotations for `secret`, `affiliate_id`, `user_ip`, `api_version`, `base_url`, `_logger`, and `_enable_logging`
   - Added type annotation for class variable `BASE_URL`

2. **SideShiftClient class attributes:**
   - Added type annotations for `timeout`, `max_connections`, `max_keepalive_connections`, `max_request_size`, `max_response_size`, `verify_ssl`, `proxy`, `max_retries`, and `_session`

3. **AsyncSideShiftClient class attributes:**
   - Added type annotations for `timeout`, `max_connections`, `max_keepalive_connections`, `verify_ssl`, `proxy`, `max_retries`, `max_request_size`, `max_response_size`, and `_client`

4. **Import updates:**
   - Added `import logging` to support the `logging.Logger` type annotation

### Benefits

- Improved type safety and static type checking support
- Better IDE autocomplete and type inference
- Clearer code documentation through explicit type information
- Enables more comprehensive mypy type checking

All existing tests pass, confirming that the type annotations are correct and do not affect runtime behavior.

