## Issue #46: [2.14] No Enum for Shift Status

### Problem
The `status` field in the `Shift` model is a plain `str`, which doesn't provide type safety or IDE autocomplete for valid status values. Users have to know the valid status strings ("waiting", "complete", "multiple", "refunded") by heart.

### Proposed Solution
Create a `ShiftStatus` enum with the known status values:
- `WAITING = "waiting"`
- `COMPLETE = "complete"`
- `MULTIPLE = "multiple"`
- `REFUNDED = "refunded"`

Update the `Shift` model to use `ShiftStatus` instead of `str` for the `status` field. Export the enum in `__init__.py` so users can import and use it.

Benefits:
- Type safety - IDE and type checkers will catch invalid status values
- Better autocomplete support
- Self-documenting code
- Easier refactoring if status values change

