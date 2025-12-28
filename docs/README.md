# SideShift SDK Documentation

This directory contains documentation for the SideShift Python SDK.

## Contents

- **[API Documentation](SIDESHIFT_API_DOCUMENTATION.md)** - Complete API reference for all SideShift.ai V2 endpoints
- **[Examples](examples/)** - Code examples demonstrating SDK usage

## Quick Start

### Installation

```bash
pip install sideshift-sdk
```

### Basic Usage

```python
from sideshift_sdk import SideShiftClient
from sideshift_sdk.endpoints import coins, pairs, quotes, shifts

# Initialize client
client = SideShiftClient(
    secret="your-secret-key",
    affiliate_id="your-affiliate-id"
)

# Get available coins
coins_list = coins.get_coins(client)
print(f"Available coins: {len(coins_list)}")

# Get pair information
pair_info = pairs.get_pair(
    client,
    from_coin="btc",
    to_coin="eth",
    affiliate_id="your-affiliate-id"
)
print(f"Rate: {pair_info.rate}, Min: {pair_info.min}, Max: {pair_info.max}")

# Request a quote
quote = quotes.request_quote(
    client,
    deposit_coin="btc",
    settle_coin="eth",
    deposit_amount="0.1",
    affiliate_id="your-affiliate-id"
)
print(f"Quote ID: {quote.id}, Rate: {quote.rate}")

# Create a fixed shift
shift = shifts.create_fixed_shift(
    client,
    quote_id=quote.id,
    settle_address="0x...",
    affiliate_id="your-affiliate-id"
)
print(f"Shift ID: {shift.id}, Deposit Address: {shift.deposit_address}")
```

### Async Usage

```python
import asyncio
from sideshift_sdk import AsyncSideShiftClient
from sideshift_sdk.endpoints import coins, pairs, quotes, shifts

async def main():
    async with AsyncSideShiftClient(
        secret="your-secret-key",
        affiliate_id="your-affiliate-id"
    ) as client:
        # Get coins
        coins_list = await coins.get_coins_async(client)
        
        # Get pair info
        pair_info = await pairs.get_pair_async(
            client,
            from_coin="btc",
            to_coin="eth"
        )
        
        # Request quote
        quote = await quotes.request_quote_async(
            client,
            deposit_coin="btc",
            settle_coin="eth",
            deposit_amount="0.1"
        )
        
        # Create shift
        shift = await shifts.create_fixed_shift_async(
            client,
            quote_id=quote.id,
            settle_address="0x..."
        )

asyncio.run(main())
```

## Authentication

The SDK supports authentication via:

1. **Constructor parameters:**
   ```python
   client = SideShiftClient(secret="...", affiliate_id="...")
   ```

2. **Environment variables:**
   ```bash
   export SIDESHIFT_SECRET="your-secret"
   export AFFILIATE_ID="your-affiliate-id"
   export SIDESHIFT_USER_IP="user-ip-address"  # Optional, for server-side
   ```

## Error Handling

```python
from sideshift_sdk.exceptions import (
    SideShiftAPIError,
    SideShiftAuthenticationError,
    SideShiftRateLimitError,
)

try:
    shift = shifts.create_fixed_shift(client, quote_id="...", settle_address="...")
except SideShiftAuthenticationError:
    print("Authentication failed")
except SideShiftRateLimitError as e:
    print(f"Rate limited. Retry after: {e.response_data}")
except SideShiftAPIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

## Rate Limiting

The SDK automatically handles rate limits with exponential backoff. Rate limits:
- **Shifts:** 5 per minute
- **Quotes:** 20 per minute

## Endpoint Coverage

The SDK provides 100% coverage of all SideShift.ai V2 API endpoints:

### Coins
- `get_coins()` - List all available coins
- `get_coin_icon()` - Get coin icon image

### Pairs
- `get_pair()` - Get pair information (min, max, rate)
- `get_pairs()` - Get multiple pairs information

### Quotes
- `request_quote()` - Request a quote for fixed rate shift

### Shifts
- `get_shift()` - Get shift information
- `get_bulk_shifts()` - Get multiple shifts
- `get_recent_shifts()` - Get recent completed shifts
- `create_fixed_shift()` - Create fixed rate shift
- `create_variable_shift()` - Create variable rate shift
- `set_refund_address()` - Set refund address for shift
- `cancel_order()` - Cancel an order

### Account
- `get_account()` - Get account information
- `get_permissions()` - Check permissions
- `get_xai_stats()` - Get XAI statistics

### Checkout
- `get_checkout()` - Get checkout information
- `create_checkout()` - Create a checkout

## Type Safety

All responses are validated using Pydantic models, providing:
- Type checking
- Runtime validation
- IDE autocomplete
- Clear error messages

## Examples

See the [examples directory](examples/) for complete working examples:
- Basic usage
- Async usage
- Error handling
- Fixed rate shifts
- Variable rate shifts
- Checkout creation

