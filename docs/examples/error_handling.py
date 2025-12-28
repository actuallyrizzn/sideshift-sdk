"""Error handling examples for SideShift SDK."""

from sideshift_sdk import SideShiftClient
from sideshift_sdk.endpoints import quotes, shifts
from sideshift_sdk.exceptions import (
    SideShiftAPIError,
    SideShiftAuthenticationError,
    SideShiftForbiddenError,
    SideShiftNotFoundError,
    SideShiftRateLimitError,
)


def example_error_handling():
    """Example: Handle various API errors."""
    client = SideShiftClient(
        secret="your-secret-key",
        affiliate_id="your-affiliate-id",
    )

    try:
        # This might fail for various reasons
        quote = quotes.request_quote(
            client,
            deposit_coin="btc",
            settle_coin="eth",
            deposit_amount="0.1",
        )

        shift = shifts.create_fixed_shift(
            client,
            quote_id=quote.id,
            settle_address="0x...",
        )

    except SideShiftAuthenticationError:
        print("Error: Authentication failed. Check your secret key.")
    except SideShiftForbiddenError:
        print("Error: Access forbidden. Check your permissions.")
    except SideShiftNotFoundError:
        print("Error: Resource not found.")
    except SideShiftRateLimitError as e:
        print(f"Error: Rate limit exceeded.")
        if e.response_data and "retry_after" in e.response_data:
            print(f"Retry after {e.response_data['retry_after']} seconds")
    except SideShiftAPIError as e:
        print(f"Error: API returned {e.status_code}: {e.message}")
        if e.response_data:
            print(f"Response: {e.response_data}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def example_validate_before_request():
    """Example: Validate inputs before making requests."""
    client = SideShiftClient(
        secret="your-secret-key",
        affiliate_id="your-affiliate-id",
    )

    # Validate that we have required parameters
    deposit_amount = "0.1"
    settle_amount = None

    if not deposit_amount and not settle_amount:
        print("Error: Either deposit_amount or settle_amount must be provided")
        return

    try:
        quote = quotes.request_quote(
            client,
            deposit_coin="btc",
            settle_coin="eth",
            deposit_amount=deposit_amount if deposit_amount else None,
            settle_amount=settle_amount if settle_amount else None,
        )
        print(f"Quote created: {quote.id}")
    except ValueError as e:
        print(f"Validation error: {e}")
    except SideShiftAPIError as e:
        print(f"API error: {e.message}")


if __name__ == "__main__":
    example_error_handling()
    example_validate_before_request()

