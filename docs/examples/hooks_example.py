"""Example: Using request/response hooks with SideShift SDK."""

from sideshift_sdk import SideShiftClient
from sideshift_sdk.endpoints import quotes, shifts


class ClientWithHooks(SideShiftClient):
    """Client with request/response hooks for logging and monitoring."""

    def _request(
        self,
        method: str,
        endpoint: str,
        params=None,
        json_data=None,
        headers=None,
        require_auth=False,
        require_user_ip=False,
        max_retries=3,
    ):
        """Override _request to add hooks."""
        # Pre-request hook: Log request details
        self._on_request(method, endpoint, params, json_data, headers)

        # Make the actual request
        response_data = super()._request(
            method=method,
            endpoint=endpoint,
            params=params,
            json_data=json_data,
            headers=headers,
            require_auth=require_auth,
            require_user_ip=require_user_ip,
            max_retries=max_retries,
        )

        # Post-response hook: Log response details
        self._on_response(method, endpoint, response_data)

        return response_data

    def _on_request(self, method: str, endpoint: str, params, json_data, headers):
        """Pre-request hook - called before making the request.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON body data
            headers: Request headers
        """
        print(f"[REQUEST] {method} {endpoint}")
        if params:
            print(f"  Params: {params}")
        if json_data:
            print(f"  Body: {json_data}")

    def _on_response(self, method: str, endpoint: str, response_data):
        """Post-response hook - called after receiving the response.

        Args:
            method: HTTP method used
            endpoint: API endpoint
            response_data: Response data dictionary
        """
        print(f"[RESPONSE] {method} {endpoint}")
        print(
            f"  Data keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'N/A'}"
        )


def example_with_hooks():
    """Example: Using client with request/response hooks."""
    # Create client with hooks
    client = ClientWithHooks(
        secret="your-secret-key",
        affiliate_id="your-affiliate-id",
    )

    # Make requests - hooks will be called automatically
    quote = quotes.request_quote(
        client,
        deposit_coin="btc",
        settle_coin="eth",
        deposit_amount="0.1",
    )

    print(f"\nQuote ID: {quote.id}")

    # Another request - hooks called again
    shift = shifts.create_fixed_shift(
        client,
        quote_id=quote.id,
        settle_address="0x...",
    )

    print(f"\nShift ID: {shift.id}")


def example_simple_wrapper():
    """Example: Simple wrapper function for request/response hooks."""
    client = SideShiftClient(
        secret="your-secret-key",
        affiliate_id="your-affiliate-id",
    )

    def make_request_with_logging(endpoint_func, *args, **kwargs):
        """Wrapper that adds logging around API calls."""
        print(f"[CALL] {endpoint_func.__name__}")
        print(f"  Args: {args}")
        print(f"  Kwargs: {kwargs}")

        # Make the actual API call
        result = endpoint_func(*args, **kwargs)

        print(f"[RESULT] {endpoint_func.__name__}")
        print(f"  Result type: {type(result).__name__}")

        return result

    # Use the wrapper
    quote = make_request_with_logging(
        quotes.request_quote,
        client,
        deposit_coin="btc",
        settle_coin="eth",
        deposit_amount="0.1",
    )

    print(f"Quote ID: {quote.id}")


if __name__ == "__main__":
    # Uncomment to run examples:
    # example_with_hooks()
    # example_simple_wrapper()
    pass
