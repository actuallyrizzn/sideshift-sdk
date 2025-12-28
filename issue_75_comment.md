## Issue #75: No Streaming Support - Solution

**Problem**: No support for streaming large responses or chunked data.

**Solution**: Added streaming methods to both sync and async clients:
- `stream_get()` / `stream_get_async()` - Stream GET responses chunk by chunk
- `stream_post()` / `stream_post_async()` - Stream POST responses chunk by chunk
- Returns iterator/generator that yields chunks
- Useful for large responses or future streaming endpoints

**Implementation**:
- Uses `stream=True` for requests library (sync)
- Uses `stream=True` for httpx (async)
- Yields chunks as they arrive
- Handles errors appropriately

**Usage**:
```python
# Sync
for chunk in client.stream_get("/large-endpoint"):
    process_chunk(chunk)

# Async
async for chunk in client.stream_get_async("/large-endpoint"):
    await process_chunk(chunk)
```

**Note**: The SideShift API currently doesn't have streaming endpoints, but this provides a foundation for future use or for handling large binary responses efficiently.

