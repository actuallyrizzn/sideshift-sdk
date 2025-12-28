## Proposed Solution for Issue #62: No Tests for Connection Errors

### Problem
While there are some basic connection error tests, we lack comprehensive coverage of connection error scenarios. The SDK should be tested for various connection failure types and edge cases.

### Solution
I will create a comprehensive test file `tests/test_connection_errors.py` that covers:

1. **Different Connection Error Types**:
   - DNS resolution failures
   - Connection refused errors
   - Unreachable hosts
   - Network unreachable errors
   - SSL/TLS connection errors

2. **Connection Errors with Retries**:
   - Connection errors that should trigger retries
   - Connection errors that fail after all retries

3. **Connection Errors Across Different Scenarios**:
   - Different HTTP methods (GET, POST, etc.)
   - Different endpoints
   - With and without authentication
   - With request IDs

4. **Connection Errors with Hooks**:
   - Verify error hooks are called for connection errors

5. **Connection Errors with Configuration**:
   - Different timeout settings
   - With proxy configuration
   - With SSL verification settings

6. **Async vs Sync**:
   - Both async and sync clients handle connection errors correctly

### Implementation Plan
- Create `tests/test_connection_errors.py` with comprehensive test coverage
- Use `responses` library and direct exception raising for sync tests
- Use `httpx` patching for async tests
- Ensure all connection error scenarios are properly tested

