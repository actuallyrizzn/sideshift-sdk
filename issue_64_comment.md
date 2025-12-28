## Proposed Solution for Issue #64: No Performance Tests

### Problem
The SDK lacks performance tests to ensure that performance characteristics remain acceptable and to catch performance regressions.

### Solution
I will create a comprehensive test file `tests/test_performance.py` that includes:

1. **Request Latency Tests**:
   - Measure single request latency
   - Verify latency is within acceptable bounds
   - Test both sync and async clients

2. **Connection Pooling Performance**:
   - Verify that connection pooling improves performance for multiple requests
   - Test that reused connections are faster than new connections

3. **Concurrent Request Performance**:
   - Verify that concurrent async requests are faster than sequential requests
   - Measure throughput improvements

4. **Memory Usage Tests**:
   - Verify memory usage doesn't grow unbounded
   - Test that clients can be created and destroyed without memory leaks

5. **Pydantic Parsing Overhead**:
   - Measure parsing overhead
   - Verify it's within acceptable bounds

6. **Bulk Operations Performance**:
   - Test performance of bulk operations vs individual operations

### Implementation Plan
- Create `tests/test_performance.py` with performance tests
- Use `time` module for timing measurements
- Use `pytest-benchmark` if available, or simple timing assertions
- Set reasonable performance thresholds
- Tests should be fast enough to run in CI

