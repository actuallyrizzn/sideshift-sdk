# SideShift Python SDK

A complete Python SDK for the [SideShift.ai](https://sideshift.ai) REST API V2, providing 100% endpoint coverage with both synchronous and asynchronous support.

## Features

- ✅ **100% API Coverage** - All 17 V2 endpoints implemented
- 🔄 **Sync & Async** - Use `SideShiftClient` or `AsyncSideShiftClient`
- 🛡️ **Type Safe** - Pydantic models for all requests and responses
- ⚡ **Rate Limiting** - Automatic retry with exponential backoff
- 🔐 **Authentication** - Support for environment variables and direct configuration
- 📚 **Well Documented** - Comprehensive docs and examples

## Installation

```bash
pip install sideshift-sdk
```

Or from source:

```bash
git clone https://github.com/actuallyrizzn/sideshift-sdk.git
cd sideshift-sdk
pip install -e .
```

## Quick Start

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
pair = pairs.get_pair(client, from_coin="btc", to_coin="eth")
print(f"Rate: {pair.rate}, Min: {pair.min}, Max: {pair.max}")

# Request a quote for fixed rate shift
quote = quotes.request_quote(
    client,
    deposit_coin="btc",
    settle_coin="eth",
    deposit_amount="0.1",
    deposit_network="bitcoin",
    settle_network="mainnet"
)

# Create a fixed shift
shift = shifts.create_fixed_shift(
    client,
    quote_id=quote.id,
    settle_address="0xde2642b2120fd3011fe9659688f76e9E4676F472"
)

print(f"Shift ID: {shift.id}")
print(f"Deposit Address: {shift.deposit_address}")
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
        pair = await pairs.get_pair_async(client, from_coin="btc", to_coin="eth")
        
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

You can provide credentials in three ways:

### 1. Constructor Parameters

```python
client = SideShiftClient(
    secret="your-secret-key",
    affiliate_id="your-affiliate-id",
    user_ip="1.2.3.4"  # Optional, for server-side integrations
)
```

### 2. Environment Variables

```bash
export SIDESHIFT_SECRET="your-secret-key"
export AFFILIATE_ID="your-affiliate-id"
export SIDESHIFT_USER_IP="user-ip-address"  # Optional
```

```python
client = SideShiftClient()  # Uses environment variables
```

### 3. Mixed (Constructor + Environment)

```python
client = SideShiftClient(
    secret="explicit-secret",  # Overrides env var
    # affiliate_id will use SIDESHIFT_AFFILIATE_ID if not provided
)
```

## API Coverage

### Coins
- `get_coins()` - List all available coins and networks
- `get_coin_icon()` - Get coin icon (SVG/PNG)

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

The SDK automatically handles rate limits with exponential backoff:

- **Shifts:** Maximum 5 per minute
- **Quotes:** Maximum 20 per minute

When rate limited, the SDK will automatically retry with exponential backoff (up to 3 retries by default).

## Type Safety

All API responses are validated using Pydantic models, providing:

- ✅ Type checking at development time
- ✅ Runtime validation
- ✅ IDE autocomplete
- ✅ Clear error messages

```python
from sideshift_sdk.models import Shift, Quote

quote: Quote = quotes.request_quote(...)  # Fully typed
shift: Shift = shifts.create_fixed_shift(...)  # Fully typed
```

## Documentation

- **[API Documentation](docs/SIDESHIFT_API_DOCUMENTATION.md)** - Complete API reference
- **[SDK Usage Guide](docs/README.md)** - SDK-specific documentation
- **[Examples](docs/examples/)** - Working code examples

## Requirements

- Python 3.8+
- `requests>=2.31.0` (for sync client)
- `httpx>=0.25.0` (for async client)
- `pydantic>=2.0.0` (for models)

## Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black sideshift_sdk tests

# Lint code
ruff check sideshift_sdk tests

# Type checking
mypy sideshift_sdk
```

## License

MIT

## Support

- **Documentation:** [docs.sideshift.ai](https://docs.sideshift.ai)
- **GitHub Issues:** [github.com/actuallyrizzn/sideshift-sdk/issues](https://github.com/actuallyrizzn/sideshift-sdk/issues)
- **Developer Chat:** [Telegram](https://t.me/joinchat/UuTn4HeK-2EUG1zZ)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

