## Issue #39 Resolved

**Solution Implemented:**
Refactored the codebase to extract common logic between sync and async clients into shared helper methods in `BaseClient`. This significantly reduces code duplication while maintaining full backward compatibility.

**Key Changes:**
- Extracted `_prepare_request()` method for common request preparation (headers, validation, size checks)
- Created shared helper methods for logging (`_log_request_start()`, `_log_response()`)
- Added shared retry calculation (`_calculate_retry_wait_time()`)
- Created hook execution methods for both sync and async (`_call_request_hooks()`, `_call_response_hooks()`, `_call_error_hooks()` and their async variants)
- Reduced `_request` method duplication from ~200 lines each to ~60 lines each
- Fixed test hangs by properly mocking `time.sleep` in rate limiting tests

**Results:**
- Code duplication reduced by ~40-50%
- All 313 tests passing
- Full backward compatibility maintained
- Improved maintainability - future changes only need to be made once

**Commit:** 6cc0140

