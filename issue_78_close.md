## Issue #78: [3.23] Missing Retry-After Header Parsing - RESOLVED

This issue has been fixed. The Retry-After header parsing now supports both integer (seconds) and HTTP-date formats per RFC 7231, and the retry logic uses the Retry-After value when available.

**Commit:** eee7bc23d01db3c850982749077a128386e924e3

**Ada's Response:**
> Acknowledged. Issue #78 is resolved:
> 
> - Retry-After header parsing now supports both integer (seconds) and HTTP-date formats per RFC 7231.
> - Retry logic uses the Retry-After value from the response when present; otherwise, it defaults to exponential backoff.
> - retry_after is extracted from the exception's response_data and governs wait timing.
> - Tests verify correct parsing and behavior in all supported formats.
> - All tests pass.
> 
> No further action is required for this fix unless additional retry timing, header parsing, or rate limit handling issues arise. Continue with remaining issues and report if regressions or new requirements are detected.


