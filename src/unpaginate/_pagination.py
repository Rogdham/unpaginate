import sys
from typing import Generic, final

if sys.version_info < (3, 13):  # pragma: no cover
    from typing_extensions import TypeVar  # for 'default' parameter
else:  # pragma: no cover
    from typing import TypeVar


C_co = TypeVar("C_co", covariant=True, default=None)


@final
class Pagination(Generic[C_co]):
    __slots__ = ["_page", "_offset", "is_last_page", "context"]

    def __init__(self, *, page: int, offset: int, context: C_co) -> None:
        self._page = page
        self._offset = offset
        self.is_last_page = False
        self.context = context

    @property
    def page(self) -> int:
        return self._page

    @property
    def offset(self) -> int:
        return self._offset

    def __repr__(self) -> str:
        return (
            "Pagination("
            f"page={self.page!r}, "
            f"offset={self.offset!r}, "
            f"is_last_page={self.is_last_page!r}, "
            f"context={self.context!r})"
        )
