# Error Code Reference

Complete reference for all error codes and exceptions in the SideShift SDK.

## Exception Hierarchy

```
SideShiftException (base)
├── SideShiftAPIError
│   ├── SideShiftAuthenticationError (401)
│   ├── SideShiftForbiddenError (403)
│   ├── SideShiftNotFoundError (404)
│   └── SideShiftRateLimitError (429)
```

## HTTP Status Codes

### 200 OK
- **Meaning**: Request successful
- **Exception**: None (normal response)
- **Action**: Process response data normally

### 201 Created
- **Meaning**: Resource created successfully
- **Exception**: None (normal response)
- **Action**: Process response data normally

### 204 No Content
- **Meaning**: Request successful, no content to return
- **Exception**: None (normal response)
- **Action**: Response is empty dictionary `{}`

### 400 Bad Request
- **Meaning**: Invalid request parameters
- **Exception**: `SideShiftAPIError`
- **Status Code**: 400
- **Common Causes**:
  - Missing required parameters
  - Invalid parameter values
  - Malformed request body
- **Action**: Check request parameters and fix validation errors

### 401 Unauthorized
- **Meaning**: Authentication required or invalid
- **Exception**: `SideShiftAuthenticationError`
- **Status Code**: 401
- **Common Causes**:
  - Missing or invalid secret key
  - Expired credentials
  - Incorrect authentication header
- **Action**: Verify secret key and authentication setup

### 403 Forbidden
- **Meaning**: Access denied
- **Exception**: `SideShiftForbiddenError`
- **Status Code**: 403
- **Common Causes**:
  - Insufficient permissions
  - Account restrictions
  - Invalid API endpoint access
- **Action**: Check account permissions and API access

### 404 Not Found
- **Meaning**: Resource not found
- **Exception**: `SideShiftNotFoundError`
- **Status Code**: 404
- **Common Causes**:
  - Invalid resource ID
  - Resource deleted or expired
  - Incorrect endpoint URL
- **Action**: Verify resource ID and endpoint

### 429 Too Many Requests
- **Meaning**: Rate limit exceeded
- **Exception**: `SideShiftRateLimitError`
- **Status Code**: 429
- **Common Causes**:
  - Too many requests in time window
  - Exceeding endpoint-specific limits
- **Action**: SDK automatically retries with exponential backoff
- **Response Data**: May include `retry_after` (seconds to wait)

### 500 Internal Server Error
- **Meaning**: Server error
- **Exception**: `SideShiftAPIError`
- **Status Code**: 500
- **Common Causes**:
  - Server-side issue
  - Temporary API unavailability
- **Action**: Retry request after a delay, contact support if persistent

## Exception Classes

### SideShiftException

Base exception for all SDK errors.

**Attributes**:
- `message`: Error message string
- `status_code`: HTTP status code (if applicable)
- `response_data`: Response data dictionary (if available)

### SideShiftAPIError

Generic API error for non-specific HTTP errors.

**Attributes**:
- `message`: Error message
- `status_code`: HTTP status code (400, 500, etc.)
- `response_data`: Response data dictionary

**Example**:
```python
except SideShiftAPIError as e:
    print(f"API Error {e.status_code}: {e.message}")
    print(f"Response: {e.response_data}")
```

### SideShiftAuthenticationError

Authentication failed (401).

**Attributes**:
- `message`: Error message (default: "Authentication failed")
- `status_code`: Always 401
- `response_data`: Response data dictionary

**Example**:
```python
except SideShiftAuthenticationError:
    print("Check your secret key")
```

### SideShiftForbiddenError

Access forbidden (403).

**Attributes**:
- `message`: Error message (default: "Access forbidden")
- `status_code`: Always 403
- `response_data`: Response data dictionary

**Example**:
```python
except SideShiftForbiddenError:
    print("Check your account permissions")
```

### SideShiftNotFoundError

Resource not found (404).

**Attributes**:
- `message`: Error message (default: "Resource not found")
- `status_code`: Always 404
- `response_data`: Response data dictionary

**Example**:
```python
except SideShiftNotFoundError:
    print("Resource not found - check the ID")
```

### SideShiftRateLimitError

Rate limit exceeded (429).

**Attributes**:
- `message`: Error message (default: "Rate limit exceeded")
- `status_code`: Always 429
- `response_data`: May contain `retry_after` (seconds to wait)

**Example**:
```python
except SideShiftRateLimitError as e:
    print(f"Rate limited: {e.message}")
    if e.response_data and "retry_after" in e.response_data:
        wait_time = e.response_data["retry_after"]
        print(f"Retry after {wait_time} seconds")
```

## Error Handling Patterns

### Basic Error Handling

```python
from sideshift_sdk.exceptions import (
    SideShiftAPIError,
    SideShiftAuthenticationError,
    SideShiftForbiddenError,
    SideShiftNotFoundError,
    SideShiftRateLimitError,
)

try:
    result = quotes.request_quote(client, ...)
except SideShiftAuthenticationError:
    print("Authentication failed")
except SideShiftForbiddenError:
    print("Access forbidden")
except SideShiftNotFoundError:
    print("Resource not found")
except SideShiftRateLimitError as e:
    print(f"Rate limited: {e.message}")
except SideShiftAPIError as e:
    print(f"API error {e.status_code}: {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Detailed Error Information

```python
try:
    result = shifts.create_fixed_shift(client, ...)
except SideShiftAPIError as e:
    print(f"Status Code: {e.status_code}")
    print(f"Message: {e.message}")
    print(f"Response Data: {e.response_data}")
    
    # Log for debugging
    import logging
    logging.error(f"API Error: {e.status_code} - {e.message}", extra={
        "response_data": e.response_data
    })
```

## Common Error Scenarios

### Invalid Quote ID

**Error**: `SideShiftNotFoundError` or `SideShiftAPIError` (400)
**Cause**: Quote ID doesn't exist or has expired
**Solution**: Request a new quote

### Missing Required Parameters

**Error**: `SideShiftAPIError` (400)
**Cause**: Missing required fields in request
**Solution**: Check endpoint documentation and provide all required parameters

### Network Errors

**Error**: `requests.exceptions.RequestException` or `httpx.RequestError`
**Cause**: Network connectivity issues
**Solution**: Check network connection, retry request

### Timeout Errors

**Error**: `requests.exceptions.Timeout` or `httpx.TimeoutException`
**Cause**: Request took too long
**Solution**: Increase timeout or check network conditions

## Error Response Format

API errors typically return JSON in this format:

```json
{
  "message": "Error description",
  "code": "ERROR_CODE",
  "details": {}
}
```

The SDK extracts the `message` field and includes the full response in `response_data`.

## Debugging Errors

1. **Check Exception Type**: Identify the specific exception class
2. **Check Status Code**: Review HTTP status code
3. **Check Response Data**: Examine `response_data` for additional details
4. **Check Request**: Verify request parameters and headers
5. **Enable Logging**: Use request/response hooks for detailed logging

See `docs/examples/error_handling.py` for complete error handling examples.

## Additional Resources

- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- [Rate Limit Documentation](docs/RATE_LIMITS.md)
- [API Documentation](docs/SIDESHIFT_API_DOCUMENTATION.md)

