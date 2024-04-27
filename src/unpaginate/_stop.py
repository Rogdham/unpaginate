import sys
from typing import Any, Generic, Optional, Tuple

from unpaginate._pagination import Pagination

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Callable
else:  # pragma: no cover
    from collections.abc import Callable

if sys.version_info < (3, 10):  # pragma: no cover
    from typing_extensions import TypeAlias
else:  # pragma: no cover
    from typing import TypeAlias

if sys.version_info < (3, 13):  # pragma: no cover
    from typing_extensions import TypeVar  # for 'default' parameter
else:  # pragma: no cover
    from typing import TypeVar


T_co = TypeVar(
    "T_co",
    covariant=True,
    default=Any,  # different from context TypeVar
)
_CallableStop: TypeAlias = Callable[[Pagination[T_co], Pagination[T_co]], bool]


class _UnpaginateStop(Generic[T_co]):
    __slots__ = ["_stops", "_op_is_and"]

    def __init__(
        self,
        *stops: _CallableStop[T_co],
        op_is_and: bool = False,
    ) -> None:
        self._stops = stops
        self._op_is_and = op_is_and

    def __call__(
        self,
        pagination_before: Pagination[T_co],
        pagination_after: Pagination[T_co],
        /,
    ) -> bool:
        values = (stop(pagination_before, pagination_after) for stop in self._stops)
        return all(values) if self._op_is_and else any(values)

    def _op_with(
        self,
        other: _CallableStop[T_co],
        *,
        op_is_and: bool,
        op_is_reversed: bool = False,
    ) -> "_UnpaginateStop[T_co]":
        if not callable(other):
            return NotImplemented  # type: ignore[unreachable]

        stops: Tuple[_CallableStop[T_co], ...]
        if len(self._stops) != 1 and self._op_is_and != op_is_and:
            if self._stops:  # noqa: SIM108  # ternary causes issues with mypy
                stops = (self, other)
            else:
                stops = (self,)
        else:
            stops = (*self._stops, other)

        if op_is_reversed:
            stops = (stops[-1], *stops[:-1])  # move other at beginning

        return _UnpaginateStop(*stops, op_is_and=op_is_and)

    def __or__(self, other: _CallableStop[T_co]) -> "_UnpaginateStop[T_co]":
        return self._op_with(other, op_is_and=False)

    def __and__(self, other: _CallableStop[T_co]) -> "_UnpaginateStop[T_co]":
        return self._op_with(other, op_is_and=True)

    def __ror__(self, other: _CallableStop[T_co]) -> "_UnpaginateStop[T_co]":
        return self._op_with(other, op_is_and=False, op_is_reversed=True)

    def __rand__(self, other: _CallableStop[T_co]) -> "_UnpaginateStop[T_co]":
        return self._op_with(other, op_is_and=True, op_is_reversed=True)

    def __repr__(self) -> str:
        if not self._stops:
            return "stop_always" if self._op_is_and else "stop_manual"
        op_str = " & " if self._op_is_and else " | "
        inner = op_str.join(getattr(stop, "_repr", repr(stop)) for stop in self._stops)
        return inner if len(self._stops) == 1 else f"({inner})"

    @classmethod
    def from_callable(
        cls, stop: _CallableStop[T_co], custom_repr: Optional[str] = None
    ) -> "_UnpaginateStop[T_co]":
        stop._repr = custom_repr or stop.__name__  # type: ignore[attr-defined] # noqa: SLF001
        return cls(stop)


stop_manual = _UnpaginateStop()


@_UnpaginateStop.from_callable
def stop_when_empty(
    pagination_before: Pagination[T_co],
    pagination_after: Pagination[T_co],
    /,
) -> bool:
    return pagination_before.offset == pagination_after.offset


def stop_on_page_smaller_than(page_size: int, /) -> _UnpaginateStop:
    def _stop_on_page_smaller_than_specific_size(
        pagination_before: Pagination[T_co],
        pagination_after: Pagination[T_co],
        /,
    ) -> bool:
        return pagination_after.offset - pagination_before.offset < page_size

    return _UnpaginateStop.from_callable(
        _stop_on_page_smaller_than_specific_size,
        f"stop_on_page_smaller_than({page_size})",
    )


@_UnpaginateStop.from_callable
def stop_on_falsy_context(
    pagination_before: Pagination[T_co],  # noqa: ARG001
    pagination_after: Pagination[T_co],
    /,
) -> bool:
    return not pagination_after.context


@_UnpaginateStop.from_callable
def stop_on_same_context(
    pagination_before: Pagination[T_co],
    pagination_after: Pagination[T_co],
    /,
) -> bool:
    return pagination_before.context == pagination_after.context
