## Proposed Solution for Issue #42: Missing Validation in Models

**Problem:**
The Pydantic models in the SDK lack comprehensive field-level validation. While basic type checking exists, many fields that should have constraints (non-empty strings, positive amounts, valid URLs, etc.) don't have validation, which can lead to invalid data being sent to the API.

**Proposed Solution:**
Add field-level validation to models using Pydantic's Field constraints and validators:

1. **String fields that must be non-empty:**
   - Use `Field(..., min_length=1)` for required non-empty strings
   - Use `Field(None, min_length=1)` for optional non-empty strings

2. **Amount fields (string representations of numbers):**
   - Add validators to ensure amounts are positive numbers
   - Validate format (numeric string)

3. **URL fields:**
   - Add validators to ensure URLs are valid format
   - Use `HttpUrl` type from Pydantic where appropriate

4. **Integer fields that should be positive:**
   - Use `Field(..., gt=0)` for positive integers

5. **Address fields:**
   - Ensure non-empty when required
   - Could add format validation if we know the pattern

6. **ID fields:**
   - Ensure non-empty when required

**Implementation Details:**
- Use Pydantic's `Field` constraints for simple validations (min_length, gt, etc.)
- Use `@field_validator` decorators for complex validations (amounts, URLs)
- Ensure backward compatibility - existing valid data should still work
- Add comprehensive tests for validation

**Testing:**
- Test that valid data still works
- Test that invalid data raises ValidationError with clear messages
- Test edge cases (empty strings, negative amounts, invalid URLs, etc.)

