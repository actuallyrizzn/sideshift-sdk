## Issue #43: [2.11] Deprecated Field Still Required

### Problem
The `has_memo` field in the `Coin` model is marked as deprecated (with a comment `# deprecated`), but it's still required (`Field(...)`). According to the API documentation, `hasMemo` is deprecated in favor of `networksWithMemo`. While the API may still return this field for backward compatibility, it shouldn't be required in the model since it's deprecated.

### Proposed Solution
Make the `has_memo` field optional by changing `Field(...)` to `Field(None)`. This way:
1. The model can still parse API responses that include `hasMemo` (for backward compatibility)
2. Users are not required to provide this deprecated field when constructing `Coin` objects
3. The field remains available for backward compatibility but is clearly marked as deprecated

### Implementation
- Change `has_memo: bool = Field(..., alias="hasMemo")  # deprecated` to `has_memo: bool | None = Field(None, alias="hasMemo")  # deprecated`
- Update any tests that rely on `has_memo` being required
- Ensure backward compatibility with existing API responses

