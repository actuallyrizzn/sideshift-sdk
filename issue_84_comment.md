## Investigation

Found code style inconsistencies across the codebase:
- Trailing newlines in several files
- Line length issues (some lines exceed 100 characters)
- Inconsistent formatting

## Proposed Solution

Run `black` formatter to fix all code style inconsistencies according to the project's configuration (line-length=100). This will ensure consistent formatting across all Python files in the codebase.

