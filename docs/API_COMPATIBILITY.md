# API Compatibility Matrix

This document outlines compatibility between the SideShift SDK and various dependencies, Python versions, and API versions.

## Python Version Compatibility

| SDK Version | Python 3.8 | Python 3.9 | Python 3.10 | Python 3.11 | Python 3.12 |
|-------------|------------|------------|--------------|-------------|-------------|
| 0.1.0+      | ✅         | ✅         | ✅           | ✅          | ✅          |

**Minimum Required**: Python 3.8+

## Dependency Compatibility

### Core Dependencies

| Dependency | Minimum Version | Recommended | Notes |
|------------|----------------|-------------|-------|
| requests   | 2.31.0         | Latest      | Required for sync client |
| httpx      | 0.25.0         | Latest      | Required for async client |
| pydantic   | 2.0.0          | Latest      | Required for models |

### Optional Dependencies

| Dependency      | Minimum Version | Recommended | Notes                          |
|----------------|----------------|-------------|--------------------------------|
| typing-extensions | 4.8.0      | Latest      | Required for Python < 3.11     |

## SideShift API Compatibility

| SDK Version | API V1 | API V2 | Notes                    |
|-------------|--------|--------|--------------------------|
| 0.1.0+      | ❌     | ✅     | V1 is deprecated         |

**Note**: The SDK only supports SideShift.ai REST API V2. V1 API is deprecated and not supported.

## Operating System Compatibility

The SDK is compatible with:
- ✅ Linux
- ✅ macOS
- ✅ Windows

## HTTP Client Compatibility

### Synchronous Client (SideShiftClient)
- Uses `requests` library
- Compatible with all Python versions 3.8+
- Supports standard HTTP/HTTPS protocols

### Asynchronous Client (AsyncSideShiftClient)
- Uses `httpx` library
- Requires Python 3.8+ (for async/await support)
- Supports standard HTTP/HTTPS protocols
- Supports HTTP/2 (via httpx)

## Breaking Changes

### Version 0.1.0
- Initial release
- No breaking changes (first version)

## Migration Guide

### From Manual API Calls

If migrating from direct API calls to the SDK:

1. **Install the SDK**:
   ```bash
   pip install sideshift-sdk
   ```

2. **Replace manual HTTP calls** with SDK methods:
   ```python
   # Before: Manual requests
   import requests
   response = requests.get("https://sideshift.ai/api/v2/coins")
   
   # After: SDK
   from sideshift_sdk import SideShiftClient
   from sideshift_sdk.endpoints import coins
   client = SideShiftClient()
   coins_list = coins.get_coins(client)
   ```

3. **Update error handling**:
   ```python
   # Before: Manual error handling
   if response.status_code == 401:
       # Handle auth error
   
   # After: SDK exceptions
   from sideshift_sdk.exceptions import SideShiftAuthenticationError
   try:
       # SDK call
   except SideShiftAuthenticationError:
       # Handle auth error
   ```

## Compatibility Testing

The SDK is tested against:
- Python 3.8, 3.9, 3.10, 3.11, 3.12
- Latest versions of dependencies
- All SideShift.ai API V2 endpoints

## Known Compatibility Issues

None at this time. If you encounter compatibility issues, please report them via GitHub issues.

## Future Compatibility

- The SDK will maintain backward compatibility within major versions
- Breaking changes will be documented in CHANGELOG.md
- Deprecated features will be marked and removed in future major versions

