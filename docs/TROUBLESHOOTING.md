# Troubleshooting Guide

Common issues and solutions when using the SideShift SDK.

## Installation Issues

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'sideshift_sdk'`

**Solutions**:
1. Ensure the package is installed:
   ```bash
   pip install sideshift-sdk
   ```

2. If installing from source:
   ```bash
   pip install -e .
   ```

3. Check Python version (requires Python 3.8+):
   ```bash
   python --version
   ```

### Dependency Conflicts

**Problem**: Version conflicts with dependencies

**Solutions**:
1. Use a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install sideshift-sdk
   ```

2. Check dependency versions:
   ```bash
   pip list | grep -E "requests|httpx|pydantic"
   ```

## Authentication Issues

### Authentication Failed (401)

**Problem**: `SideShiftAuthenticationError: Authentication failed`

**Solutions**:
1. Verify your secret key is correct
2. Check that the secret key is being passed correctly:
   ```python
   client = SideShiftClient(secret="your-secret-key")
   ```

3. Ensure the secret key is not expired or revoked
4. Check environment variables if using them:
   ```python
   # Verify environment variable is set
   import os
   print(os.getenv("SIDESHIFT_SECRET"))
   ```

### Forbidden (403)

**Problem**: `SideShiftForbiddenError: Access forbidden`

**Solutions**:
1. Verify your account has the necessary permissions
2. Check that you're using the correct API endpoint
3. Ensure your account is not restricted

## Rate Limiting Issues

### Rate Limit Exceeded (429)

**Problem**: `SideShiftRateLimitError: Rate limit exceeded`

**Solutions**:
1. The SDK automatically retries with exponential backoff
2. Reduce request frequency:
   - Shifts: Maximum 5 per minute
   - Quotes: Maximum 20 per minute
3. Implement request queuing for high-volume applications
4. Check `retry_after` in the exception's `response_data`:
   ```python
   except SideShiftRateLimitError as e:
       if e.response_data and "retry_after" in e.response_data:
           wait_time = e.response_data["retry_after"]
           print(f"Retry after {wait_time} seconds")
   ```

## Network Issues

### Connection Errors

**Problem**: Connection timeouts or network errors

**Solutions**:
1. Check your internet connection
2. Verify firewall/proxy settings
3. Increase timeout if needed:
   ```python
   client = SideShiftClient(secret="...", timeout=60)
   ```
4. Check if the API is accessible:
   ```bash
   curl https://sideshift.ai/api/v2/coins
   ```

### SSL/TLS Errors

**Problem**: SSL certificate verification errors

**Solutions**:
1. Ensure your system's CA certificates are up to date
2. Check system time is correct (SSL certificates are time-sensitive)
3. If behind a corporate proxy, configure proxy settings (not currently supported in SDK)

## Data Validation Issues

### Validation Errors

**Problem**: `ValidationError` from Pydantic models

**Solutions**:
1. Check that required fields are provided
2. Verify data types match expected types
3. Check field names match API requirements
4. Review model documentation for required fields

### Missing Required Fields

**Problem**: `ValueError` or validation errors for missing fields

**Solutions**:
1. Review endpoint documentation for required parameters
2. Check that affiliate_id is provided when required
3. Ensure either deposit_amount or settle_amount is provided for quotes

## Async Issues

### Async Context Manager Errors

**Problem**: Errors when using async client

**Solutions**:
1. Always use async context manager:
   ```python
   async with AsyncSideShiftClient(secret="...") as client:
       # Use client
       pass
   ```

2. Ensure you're awaiting async calls:
   ```python
   quote = await quotes.request_quote_async(client, ...)
   ```

3. Use `asyncio.run()` for top-level async code:
   ```python
   import asyncio
   
   async def main():
       async with AsyncSideShiftClient(secret="...") as client:
           # Your code
           pass
   
   asyncio.run(main())
   ```

## Type Checking Issues

### MyPy Errors

**Problem**: Type checking errors with mypy

**Solutions**:
1. Ensure type hints are correct
2. Use type aliases from `sideshift_sdk.types`:
   ```python
   from sideshift_sdk.types import JsonDict, HeadersDict
   ```

3. Check mypy configuration in `pyproject.toml`

## Common Error Patterns

### "Unknown error" Messages

**Problem**: Generic error messages without details

**Solutions**:
1. Check the exception's `response_data` attribute for more details
2. Enable logging to see full error details
3. Check network connectivity and API status

### Empty Responses

**Problem**: Empty dictionaries or None values

**Solutions**:
1. Check API endpoint documentation for expected response format
2. Verify request parameters are correct
3. Check that the resource exists (for GET requests)

## Getting Help

If you're still experiencing issues:

1. Check the [documentation](README.md)
2. Review [examples](docs/examples/)
3. Search [existing issues](https://github.com/actuallyrizzn/sideshift-sdk/issues)
4. Create a new issue with:
   - Python version
   - SDK version
   - Error message and traceback
   - Steps to reproduce
   - Code example (sanitized, no secrets)

## Debugging Tips

1. **Enable verbose logging** (if logging is implemented)
2. **Use request/response hooks** to inspect requests/responses (see `docs/examples/hooks_example.py`)
3. **Check response data** in exceptions:
   ```python
   except SideShiftAPIError as e:
       print(f"Status: {e.status_code}")
       print(f"Message: {e.message}")
       print(f"Response Data: {e.response_data}")
   ```
4. **Test with minimal example** to isolate the issue
5. **Verify API credentials** work with curl or Postman

