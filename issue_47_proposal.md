## Issue #47: [2.15] Unused Utility Function

### Problem
Some utility functions in `sideshift_sdk/utils.py` are defined but never used in the codebase. This adds unnecessary code and maintenance burden.

### Proposed Solution
Identify and remove unused utility functions. Based on my analysis:
- `handle_rate_limit` - appears to be unused (rate limit handling is done inline in client.py)
- `build_coin_network` - appears to be unused (coin-network building is done inline where needed)

### Implementation
1. Search the codebase for usages of each utility function
2. Remove functions that are not used anywhere
3. Remove corresponding tests if the function is removed
4. Update any imports that reference removed functions

