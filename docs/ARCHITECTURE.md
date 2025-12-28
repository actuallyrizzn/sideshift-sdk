# SideShift SDK Architecture

This document describes the architecture and design decisions of the SideShift SDK.

## Overview

The SideShift SDK is a Python client library for the SideShift.ai REST API V2. It provides both synchronous and asynchronous interfaces for interacting with the API.

## Core Components

### 1. Client Classes

#### BaseClient
- **Location**: `sideshift_sdk/client.py`
- **Purpose**: Base class containing shared functionality between sync and async clients
- **Key Features**:
  - Header management (`_get_headers`, `_merge_headers`)
  - Request preparation (`_prepare_request`)
  - Request/response validation
  - Logging infrastructure
  - Hook system (request, response, error hooks)
  - Request deduplication
  - Metrics tracking
  - Circuit breaker pattern
  - Response caching

#### SideShiftClient (Synchronous)
- **Location**: `sideshift_sdk/client.py`
- **Purpose**: Synchronous client using `requests` library
- **Key Features**:
  - Connection pooling via `requests.Session`
  - Thread-safe operations
  - Context manager support
  - Batch request methods
  - Streaming support

#### AsyncSideShiftClient (Asynchronous)
- **Location**: `sideshift_sdk/client.py`
- **Purpose**: Asynchronous client using `httpx` library
- **Key Features**:
  - Async connection pooling via `httpx.AsyncClient`
  - Async context manager support
  - Concurrent request support
  - Async batch methods
  - Async streaming support

### 2. Endpoint Modules

Endpoints are organized by domain:
- `account.py` - Account information
- `checkout.py` - Checkout operations
- `coins.py` - Coin and network information
- `pairs.py` - Trading pair information
- `quotes.py` - Quote requests
- `shifts.py` - Shift operations

Each module provides both sync and async versions of functions.

### 3. Models

- **Location**: `sideshift_sdk/models.py`
- **Purpose**: Pydantic models for request/response validation
- **Benefits**:
  - Type safety
  - Automatic validation
  - Clear API contracts

### 4. Exceptions

- **Location**: `sideshift_sdk/exceptions.py`
- **Purpose**: Custom exception hierarchy for API errors
- **Types**:
  - `SideShiftException` (base)
  - `SideShiftAPIError` (4xx/5xx errors)
  - `SideShiftAuthenticationError` (401)
  - `SideShiftForbiddenError` (403)
  - `SideShiftNotFoundError` (404)
  - `SideShiftRateLimitError` (429)
  - `SideShiftNetworkError` (network issues)
  - `SideShiftSizeLimitError` (request/response size exceeded)

## Design Patterns

### 1. Request Deduplication

**Purpose**: Prevent duplicate API calls when the same request is made concurrently.

**Implementation**:
- Creates a request key from method, endpoint, params, and body
- Tracks in-flight requests
- Reuses futures/promises for duplicate requests
- Optional response caching with TTL

**Usage**: Opt-in via `enable_request_deduplication=True`

### 2. Circuit Breaker

**Purpose**: Prevent cascading failures when the API is experiencing issues.

**States**:
- **CLOSED**: Normal operation
- **OPEN**: Too many failures, requests fail fast
- **HALF_OPEN**: Testing if service recovered

**Implementation**:
- Tracks failure count
- Opens after threshold
- Half-opens after timeout
- Closes on success

**Usage**: Opt-in via `enable_circuit_breaker()`

### 3. Request Metrics

**Purpose**: Track request statistics for monitoring and debugging.

**Metrics Tracked**:
- Total requests
- Successful/failed requests
- Rate limit errors
- Network errors
- Response times (min, max, average)

**Usage**: Opt-in via `enable_metrics()`

### 4. Retry Logic

**Purpose**: Automatically retry failed requests with exponential backoff.

**Implementation**:
- Default: 3 retries
- Exponential backoff with jitter
- Respects `Retry-After` header for rate limits
- Configurable per-request or client-wide

### 5. Hook System

**Purpose**: Allow users to intercept and modify requests/responses.

**Hook Types**:
- **Request Hooks**: Called before request is sent
- **Response Hooks**: Called after successful response
- **Error Hooks**: Called when errors occur

**Usage**: Add hooks via `add_request_hook()`, `add_response_hook()`, `add_error_hook()`

## Request Flow

### Synchronous Request

1. User calls endpoint function (e.g., `get_coins(client)`)
2. Endpoint function calls `client.get(endpoint)`
3. `client.get()` calls `client._request()`
4. `_request()`:
   - Checks circuit breaker
   - Prepares request (headers, validation)
   - Tracks metrics start
   - Makes HTTP request via `requests.Session`
   - Handles response
   - Tracks metrics completion
   - Records circuit breaker result
   - Returns response data
5. Endpoint function validates and returns model

### Asynchronous Request

1. User calls async endpoint function (e.g., `await get_coins_async(client)`)
2. Endpoint function calls `await client.get(endpoint)`
3. `client.get()` calls `await client._request()`
4. `_request()`:
   - Checks circuit breaker (async)
   - Prepares request
   - Tracks metrics start
   - Makes HTTP request via `httpx.AsyncClient`
   - Handles response
   - Tracks metrics completion
   - Records circuit breaker result
   - Returns response data
5. Endpoint function validates and returns model

## Error Handling

1. **Network Errors**: Wrapped in `SideShiftNetworkError`
2. **API Errors**: Parsed from response, raised as appropriate exception
3. **Rate Limits**: Raised as `SideShiftRateLimitError` with retry information
4. **Size Limits**: Raised as `SideShiftSizeLimitError`
5. **Validation Errors**: Raised during request preparation

All errors include:
- Error message
- Request ID (for correlation)
- Response data (if available)
- Method and endpoint information

## Configuration

### Environment Variables

- `SIDESHIFT_SECRET` - Account secret
- `SIDESHIFT_BASE_URL` - Base API URL
- `SIDESHIFT_API_VERSION` - API version
- `SIDESHIFT_TIMEOUT` - Request timeout
- `SIDESHIFT_MAX_RETRIES` - Max retry count
- `SIDESHIFT_MAX_CONNECTIONS` - Connection pool size
- `SIDESHIFT_VERIFY_SSL` - SSL verification
- `SIDESHIFT_PROXY` - Proxy configuration

### Client Parameters

All environment variables can be overridden via constructor parameters.

## Thread Safety

- **Sync Client**: Thread-safe (uses `requests.Session` with connection pooling)
- **Async Client**: Safe for concurrent async operations (uses `httpx.AsyncClient`)

## Performance Considerations

1. **Connection Pooling**: Both clients maintain connection pools
2. **Request Deduplication**: Reduces duplicate API calls
3. **Response Caching**: Optional caching with TTL
4. **Batch Requests**: Efficient handling of multiple requests
5. **Concurrent Requests**: Async client supports concurrent operations

## Extension Points

1. **Hooks**: Custom request/response/error handling
2. **Subclassing**: Extend clients for custom behavior
3. **Metrics**: Track custom metrics via hook system
4. **Custom Exceptions**: Raise custom exceptions from hooks

## Testing

- Unit tests for all components
- Integration tests with mock server
- Concurrent request tests
- Error handling tests
- Performance tests

## Future Enhancements

- Full sync support for request deduplication
- Enhanced pagination when API adds support
- WebSocket support (if API adds it)
- Request/response compression
- Advanced caching strategies

