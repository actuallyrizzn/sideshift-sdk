## Problem Description

While most internal methods have docstrings, some could be more comprehensive:

1. **Context manager methods** (`__enter__`, `__exit__`, `__aenter__`, `__aexit__`) have minimal docstrings
2. **`close()` methods** could be more detailed about what they do
3. **Internal helper methods** could benefit from more detailed documentation about their behavior, edge cases, and usage

## Proposed Solution

1. Enhance docstrings for context manager methods to explain their purpose and behavior
2. Improve `close()` method docstrings to explain resource cleanup
3. Add more detailed documentation to internal methods where helpful
4. Ensure all internal methods follow consistent docstring format (Args, Returns, Raises sections where applicable)

