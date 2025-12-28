# Performance Considerations

This document outlines performance considerations and best practices when using the SideShift SDK.

## Connection Pooling

The SDK uses connection pooling for HTTP requests:

- **Synchronous Client**: Uses `requests.Session()` which maintains a connection pool
- **Asynchronous Client**: Uses `httpx.AsyncClient()` which also maintains a connection pool

### Best Practices

1. **Reuse Client Instances**: Create a client once and reuse it for multiple requests
   ```python
   # Good: Reuse client
   client = SideShiftClient(secret="...")
   quote1 = quotes.request_quote(client, ...)
   quote2 = quotes.request_quote(client, ...)
   
   # Avoid: Creating new clients for each request
   ```

2. **Use Context Managers**: Ensure proper cleanup
   ```python
   with SideShiftClient(secret="...") as client:
       # Make requests
       pass
   # Client automatically closed
   ```

3. **Async Client**: Use async context managers for async operations
   ```python
   async with AsyncSideShiftClient(secret="...") as client:
       # Make async requests
       pass
   ```

## Rate Limiting

The SDK automatically handles rate limits with exponential backoff:

- **Shifts**: Maximum 5 per minute
- **Quotes**: Maximum 20 per minute
- **Default retries**: 3 attempts with exponential backoff

### Performance Impact

- Rate limit retries add latency to requests
- Consider implementing request queuing for high-volume applications
- Monitor rate limit errors to optimize request patterns

## Concurrent Requests

### Async Client

The async client supports concurrent requests:

```python
async with AsyncSideShiftClient(secret="...") as client:
    # Run multiple requests concurrently
    results = await asyncio.gather(
        coins.get_coins_async(client),
        account.get_account_async(client),
        pairs.get_pairs_async(client, pairs=["btc-mainnet", "eth-mainnet"]),
    )
```

**Performance Benefit**: Concurrent requests can significantly reduce total request time.

### Sync Client

The sync client processes requests sequentially. For concurrent operations, use:
- Thread pools for I/O-bound operations
- Process pools for CPU-bound operations (not recommended for this SDK)

## Request Timeouts

Default timeout is 30 seconds. Adjust based on your needs:

```python
client = SideShiftClient(secret="...", timeout=60)  # 60 second timeout
```

**Considerations**:
- Longer timeouts allow for slower networks but increase wait time on failures
- Shorter timeouts fail faster but may timeout on legitimate slow responses

## Response Parsing

All responses are parsed using Pydantic models:

- **Validation overhead**: Minimal, but adds some processing time
- **Type safety**: Provides runtime validation and type checking
- **Error handling**: Invalid responses are caught early

## Memory Usage

- **Client instances**: Minimal memory footprint
- **Response objects**: Pydantic models are lightweight
- **Connection pools**: Managed automatically

## Best Practices Summary

1. ✅ Reuse client instances
2. ✅ Use async client for concurrent operations
3. ✅ Implement proper error handling
4. ✅ Monitor rate limits
5. ✅ Use appropriate timeouts
6. ✅ Close clients when done (or use context managers)
7. ✅ Batch operations when possible
8. ✅ Cache frequently accessed data (coins, pairs) when appropriate

## Performance Monitoring

Consider implementing:

- Request timing/logging
- Rate limit monitoring
- Error rate tracking
- Response time metrics

See `docs/examples/hooks_example.py` for examples of implementing request/response hooks for monitoring.

