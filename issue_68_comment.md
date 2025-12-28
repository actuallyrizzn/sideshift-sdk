# Issue #68: [3.13] Missing Type Stubs

## Solution

Added type stub support by creating a `py.typed` marker file and updating the build configuration to include it in the package distribution.

### Changes Made

1. **Created `sideshift_sdk/py.typed` marker file:**
   - This empty marker file tells type checkers (like mypy, pyright, etc.) that the package has inline type annotations
   - Follows PEP 561 standard for type checking support

2. **Updated `pyproject.toml`:**
   - Added `package-data = {"sideshift_sdk" = ["py.typed"]}` to ensure the marker file is included in the built package
   - This ensures that when the package is installed, type checkers can find the marker file

### Benefits

- Type checkers will now recognize the package as having type information
- Better IDE support for type checking and autocomplete
- Enables proper type checking for downstream projects using this SDK
- Follows Python packaging best practices (PEP 561)

The package already has comprehensive inline type annotations (as added in Issue #67), so the `py.typed` marker file is sufficient. No separate `.pyi` stub files are needed since all type information is inline.

All existing tests pass, confirming that the marker file does not affect runtime behavior.

