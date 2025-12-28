## Issue #44: [2.12] Required affiliate_id in QuoteRequest

### Problem
The `affiliate_id` field in `QuoteRequest` is required (`Field(..., min_length=1)`), but the endpoint function `request_quote` allows it to be `None` and falls back to `client.affiliate_id` or an empty string `""`. This creates a mismatch:
1. If both `affiliate_id` parameter and `client.affiliate_id` are `None`, the code uses `""` (empty string)
2. The `QuoteRequest` model requires `affiliate_id` to be a non-empty string, so validation fails
3. The `normalize_affiliate_id` function is imported but not used in the quote endpoint

### Proposed Solution
1. Make `affiliate_id` optional in the `QuoteRequest` model (change `Field(...)` to `Field(None)`)
2. Use `normalize_affiliate_id` in the endpoint function to properly handle None/empty strings
3. Ensure that if `affiliate_id` is still None after normalization and fallback, we raise a clear error before creating the `QuoteRequest`

This approach:
- Aligns with how other endpoints handle `affiliate_id` (using `normalize_affiliate_id`)
- Allows the model to be flexible while the endpoint enforces the requirement
- Provides better error messages if `affiliate_id` is missing

