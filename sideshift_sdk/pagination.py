"""Pagination utilities for SideShift SDK.

Note: The SideShift API currently uses limit-based responses rather than
traditional pagination. This module provides helpers for working with
limit-based endpoints and can be extended when the API adds pagination support.
"""

from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from sideshift_sdk.client import AsyncSideShiftClient, SideShiftClient


class PaginatedIterator:
    """Iterator for paginated or limit-based API responses.

    This class provides a simple way to iterate through API responses
    that may be paginated in the future, or work with limit-based endpoints.
    """

    def __init__(
        self,
        fetch_page: Callable[[int, int], Any],
        page_size: int = 10,
        max_pages: int | None = None,
    ):
        """Initialize paginated iterator.

        Args:
            fetch_page: Callable that takes (page, page_size) and returns page data
            page_size: Number of items per page
            max_pages: Maximum number of pages to fetch (None = unlimited)
        """
        self._fetch_page = fetch_page
        self._page_size = page_size
        self._max_pages = max_pages
        self._current_page = 0
        self._current_items: list[Any] = []
        self._item_index = 0
        self._has_more = True

    def __iter__(self) -> "PaginatedIterator":
        """Return iterator."""
        return self

    def __next__(self) -> Any:
        """Get next item."""
        if not self._has_more:
            raise StopIteration

        # If we've exhausted current items, fetch next page
        if self._item_index >= len(self._current_items):
            self._current_page += 1
            if self._max_pages and self._current_page > self._max_pages:
                raise StopIteration

            try:
                page_data = self._fetch_page(self._current_page, self._page_size)
                if isinstance(page_data, list):
                    self._current_items = page_data
                    # If we got fewer items than requested, we've reached the end
                    if len(page_data) < self._page_size:
                        self._has_more = False
                elif isinstance(page_data, dict) and "items" in page_data:
                    self._current_items = page_data["items"]
                    self._has_more = page_data.get("has_more", len(page_data["items"]) == self._page_size)
                else:
                    self._current_items = []
                    self._has_more = False

                if not self._current_items:
                    self._has_more = False
                    raise StopIteration

                self._item_index = 0
            except Exception:
                self._has_more = False
                raise

        item = self._current_items[self._item_index]
        self._item_index += 1
        return item

    def get_all(self) -> list[Any]:
        """Fetch all pages and return as a single list.

        Returns:
            List of all items across all pages
        """
        return list(self)


def paginate_recent_shifts(
    client: "SideShiftClient", page_size: int = 10, max_pages: int | None = None
) -> PaginatedIterator:
    """Create a paginated iterator for recent shifts.

    Note: The API currently only supports limit-based fetching. This helper
    provides a foundation for future pagination support.

    Args:
        client: SideShift client instance
        page_size: Number of shifts per page (max 100)
        max_pages: Maximum number of pages to fetch (None = unlimited)

    Returns:
        PaginatedIterator for recent shifts

    Example:
        >>> for shift in paginate_recent_shifts(client, page_size=20):
        ...     print(f"Shift: {shift.id}")
    """
    from sideshift_sdk.endpoints import shifts

    def fetch_page(page: int, size: int) -> list[Any]:
        """Fetch a page of recent shifts."""
        # API uses limit parameter (max 100)
        limit = min(size, 100)
        return shifts.get_recent_shifts(client, limit=limit)

    return PaginatedIterator(fetch_page, page_size=page_size, max_pages=max_pages)


async def paginate_recent_shifts_async(
    client: "AsyncSideShiftClient", page_size: int = 10, max_pages: int | None = None
) -> PaginatedIterator:
    """Create a paginated iterator for recent shifts (async).

    Args:
        client: Async SideShift client instance
        page_size: Number of shifts per page (max 100)
        max_pages: Maximum number of pages to fetch (None = unlimited)

    Returns:
        PaginatedIterator for recent shifts

    Example:
        >>> async for shift in paginate_recent_shifts_async(client, page_size=20):
        ...     print(f"Shift: {shift.id}")
    """
    from sideshift_sdk.endpoints import shifts

    async def fetch_page(page: int, size: int) -> list[Any]:
        """Fetch a page of recent shifts."""
        limit = min(size, 100)
        return await shifts.get_recent_shifts_async(client, limit=limit)

    # For async, we need a different approach
    # For now, return a simple wrapper
    class AsyncPaginatedIterator:
        """Async version of paginated iterator."""

        def __init__(self, fetch_func: Callable, page_size: int, max_pages: int | None):
            self._fetch_func = fetch_func
            self._page_size = page_size
            self._max_pages = max_pages
            self._current_page = 0
            self._current_items: list[Any] = []
            self._item_index = 0
            self._has_more = True

        def __aiter__(self) -> "AsyncPaginatedIterator":
            return self

        async def __anext__(self) -> Any:
            if not self._has_more:
                raise StopAsyncIteration

            if self._item_index >= len(self._current_items):
                self._current_page += 1
                if self._max_pages and self._current_page > self._max_pages:
                    raise StopAsyncIteration

                try:
                    page_data = await self._fetch_func(self._current_page, self._page_size)
                    if isinstance(page_data, list):
                        self._current_items = page_data
                        if len(page_data) < self._page_size:
                            self._has_more = False
                    else:
                        self._current_items = []
                        self._has_more = False

                    if not self._current_items:
                        self._has_more = False
                        raise StopAsyncIteration

                    self._item_index = 0
                except Exception:
                    self._has_more = False
                    raise

            item = self._current_items[self._item_index]
            self._item_index += 1
            return item

        async def get_all(self) -> list[Any]:
            """Fetch all pages and return as a single list."""
            return [item async for item in self]

    return AsyncPaginatedIterator(fetch_page, page_size=page_size, max_pages=max_pages)

