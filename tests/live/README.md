# SideShift SDK Live Tests

This directory contains live test scripts that use real SideShift API credentials to test the SDK functionality against the actual API.

## Setup

### 1. Install Dependencies

Make sure you have `python-dotenv` installed:

```bash
pip install python-dotenv
```

### 2. Configure Credentials

Create a `.env` file in this directory (`tests/live/.env`) with your SideShift API credentials:

```env
SIDESHIFT_ACCOUNT_ID=your_account_id_here
SIDESHIFT_API_SECRET=your_api_secret_here
```

**Note:** The `.env` file is gitignored and will not be committed to the repository. See `.env.example` for a template.

## Test Scripts

### Individual Endpoint Tests

1. **`test_account.py`** - Tests account-related endpoints:
   - `get_account()` - Get account information
   - `get_permissions()` - Get account permissions
   - `get_xai_stats()` - Get XAI statistics

2. **`test_coins.py`** - Tests coin-related endpoints:
   - `get_coins()` - Get all available coins
   - `get_coin_icon()` - Get coin icon (binary data)

3. **`test_pairs.py`** - Tests pair-related endpoints:
   - `get_pair()` - Get single pair information
   - `get_pairs()` - Get multiple pairs information

4. **`test_quotes.py`** - Tests quote-related endpoints:
   - `request_quote()` - Request a quote for a fixed rate shift

5. **`test_shifts.py`** - Tests shift-related endpoints:
   - `get_recent_shifts()` - Get recent completed shifts
   - `get_shift()` - Get specific shift by ID
   - `get_bulk_shifts()` - Get multiple shifts by IDs

### Comprehensive Tests

6. **`test_all.py`** - Runs all tests for both sync and async clients:
   - Tests all endpoints with synchronous client
   - Tests all endpoints with asynchronous client
   - Provides comprehensive test summary

7. **`test_bridge_routes.py`** - Tests bridge routes and calculates fees/slippage:
   - Tests SOL -> BASE (ETH) bridge route
   - Tests TON -> BASE (ETH) bridge route
   - Calculates USD values and fee estimates

## Usage

Run individual test scripts:

```bash
cd tests/live
python test_account.py
python test_coins.py
python test_pairs.py
python test_quotes.py
python test_shifts.py
python test_bridge_routes.py
```

Or run the comprehensive test:

```bash
cd tests/live
python test_all.py
```

## Notes

- All scripts read credentials from the `.env` file in this directory
- Scripts use ASCII-safe output (no Unicode checkmarks) for Windows compatibility
- Scripts handle errors gracefully and provide detailed output
- The XAI stats endpoint may have model validation issues (handled in tests)
- Some endpoints (like quotes) may require `user_ip` header for full functionality

## Security

- **Never commit the `.env` file** - it contains sensitive API credentials
- The `.env` file is already in `.gitignore`
- Use `.env.example` as a template for other developers
