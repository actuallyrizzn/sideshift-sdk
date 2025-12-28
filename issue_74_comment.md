## Issue #74: Missing Pagination Support - Solution

**Problem**: No pagination helpers for endpoints that return lists of data.

**Solution**: Added pagination utilities module with:
- `PaginatedIterator` class for iterating through paginated responses
- `paginate_recent_shifts()` helper for recent shifts endpoint
- `paginate_recent_shifts_async()` async version
- Foundation for future pagination support when API adds it

**Implementation**:
- Created `sideshift_sdk/pagination.py` module
- Works with current limit-based API responses
- Can be extended when API adds page/offset parameters
- Provides `get_all()` method to fetch all pages at once

**Usage**:
```python
from sideshift_sdk import paginate_recent_shifts

# Iterate through shifts
for shift in paginate_recent_shifts(client, page_size=20):
    print(f"Shift: {shift.id}")

# Or get all at once
all_shifts = paginate_recent_shifts(client).get_all()
```

**Note**: The SideShift API currently uses limit-based responses rather than traditional pagination. This implementation provides a foundation that can be extended when the API adds pagination support.

