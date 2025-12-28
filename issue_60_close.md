## Issue #60: [3.5] Shallow Mocking in Tests - RESOLVED

### Solution Implemented

Refactored all endpoint tests in `tests/test_endpoints.py` to use deeper HTTP-level mocking instead of shallow mocking of client methods.

**For Synchronous Tests:**
- Replaced `patch.object(client, "get")` and `patch.object(client, "post")` with the `responses` library
- The `responses` library mocks at the HTTP request level, ensuring the client's internal `_request` method and its logic (header merging, error handling, retry logic, etc.) are fully exercised

**For Asynchronous Tests:**
- Replaced shallow mocking with patching `httpx.AsyncClient.request` directly
- This provides deeper mocking than patching client methods while still working with `httpx`

### Benefits

1. **Better Test Coverage**: Tests now exercise the client's internal request handling logic, not just the endpoint functions
2. **More Realistic Testing**: HTTP-level mocking simulates actual API interactions more accurately
3. **Catches More Bugs**: Issues in header merging, error handling, and other internal logic are now caught by tests

### Test Results

- All 46 endpoint tests refactored (both sync and async)
- All 216 tests in the full test suite pass
- No regressions introduced

### Commit

2caa9c23c1d2a935580b9e6c5bef681fdd363b72

