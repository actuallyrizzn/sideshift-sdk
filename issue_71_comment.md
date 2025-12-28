## Issue #71: Missing Request Metrics - Solution Implemented

**Problem**: No way to track request statistics (success rate, response times, error counts, etc.)

**Solution**: Added comprehensive request metrics tracking to BaseClient.

**Implementation**:
- `enable_metrics()` method to enable/disable metrics tracking
- `get_metrics()` method to retrieve current metrics
- `reset_metrics()` method to clear metrics
- Tracks: total requests, successful requests, failed requests, rate limit errors, network errors, response times
- Thread-safe for sync client, async-safe for async client
- Metrics are opt-in (disabled by default for backward compatibility)

**Usage**:
```python
client = SideShiftClient(secret="...")
client.enable_metrics()

# Make requests...
metrics = client.get_metrics()
print(f"Success rate: {metrics['successful_requests'] / metrics['total_requests'] * 100:.1f}%")
print(f"Average response time: {metrics['average_response_time']:.3f}s")
```

**Metrics Provided**:
- total_requests
- successful_requests
- failed_requests
- rate_limit_errors
- network_errors
- average_response_time
- min_response_time
- max_response_time

