from contextlib import suppress
from functools import wraps
from inspect import Parameter, signature
import sys
from typing import Any, Protocol, TypeVar, Union, overload

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Callable, Iterable, Iterator
else:  # pragma: no cover
    from collections.abc import Callable, Iterable, Iterator

if sys.version_info < (3, 10):  # pragma: no cover
    from typing_extensions import Concatenate, ParamSpec
else:  # pragma: no cover
    from typing import Concatenate, ParamSpec


P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")


class Pagination:
    __slots__ = ["_page", "_offset", "_finished", "context"]

    def __init__(
        self,
        *,
        page: int = 0,
        offset: int = 0,
        context: Any = None,
    ) -> None:
        self._page = page
        self._offset = offset
        self._finished = False
        self.context = context

    @property
    def page(self) -> int:
        return self._page

    @property
    def offset(self) -> int:
        return self._offset

    @property
    def finished(self) -> bool:
        return self._finished

    def finish(self) -> None:
        self._finished = True


# typing note: paginated can be applied on either functions or class methods
# for functions, the 'pagination' argument is expected to be the first parameter
# for methods, it is expected to be after the 'self' parameter
# a lot of the type complexity comes from supporting both cases

# note that as a side-effect, it works as well on functions
# where the 'pagination' argument is the second parameter


class _PaginatedDecorator(Protocol):
    @overload
    def __call__(
        self, fct: Callable[Concatenate[Pagination, P], Iterable[T]]
    ) -> Callable[P, Iterator[T]]:
        ...

    @overload
    def __call__(
        self, fct: Callable[Concatenate[U, Pagination, P], Iterable[T]]
    ) -> Callable[Concatenate[U, P], Iterator[T]]:
        ...


def paginated(
    *,
    page: int = 0,
    offset: int = 0,
    context: Any = None,
    stop_when_empty: bool = True,
) -> _PaginatedDecorator:
    @overload
    def paginated_decorator(
        fct: Callable[Concatenate[Pagination, P], Iterable[T]]
    ) -> Callable[P, Iterator[T]]:
        ...

    @overload
    def paginated_decorator(
        fct: Callable[Concatenate[U, Pagination, P], Iterable[T]]
    ) -> Callable[Concatenate[U, P], Iterator[T]]:
        ...

    def paginated_decorator(
        fct: (
            Union[
                Callable[Concatenate[Pagination, P], Iterable[T]],
                Callable[Concatenate[U, Pagination, P], Iterable[T]],
            ]
        )
    ) -> Union[Callable[P, Iterator[T]], Callable[Concatenate[U, P], Iterator[T]]]:
        if isinstance(fct, (classmethod, staticmethod)):
            return type(fct)(paginated_decorator(fct.__func__))  # type: ignore[unreachable]

        sig = signature(fct)
        parameters = tuple(sig.parameters.values())

        # make sure a pagination parameter exists at first or second position

        # while we could accept any position without much code change,
        # it would be more confusing, and we are limited by PEP 677 anyways

        for param_pos in range(2):
            try:
                param = parameters[param_pos]
            except IndexError:
                continue
            if param.name == "pagination" and param.kind in [
                Parameter.POSITIONAL_ONLY,
                Parameter.POSITIONAL_OR_KEYWORD,
            ]:
                break
        else:
            raise TypeError(
                f"Paginated function '{fct.__name__}' "
                "must have 'pagination' as first parameter"
            )

        # create wrapped function

        @wraps(fct)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> Iterator[T]:
            pagination = Pagination(page=page, offset=offset, context=context)

            try:
                arguments = sig.bind(
                    *args[:param_pos],
                    pagination,
                    *args[param_pos:],
                    **kwargs,
                )
            except TypeError as ex:
                if "pagination" in kwargs:
                    raise TypeError(
                        f"Paginated function '{fct.__name__}' "
                        "cannot be called with a 'pagination' parameter"
                    ) from ex
                raise  # pragma: no cover
            arguments.apply_defaults()

            while not pagination.finished:
                iterable = fct(*arguments.args, **arguments.kwargs)
                empty = True
                for item in iterable:
                    pagination._offset += 1  # noqa: SLF001
                    empty = False
                    yield item
                if empty and stop_when_empty:
                    pagination.finish()
                    break
                pagination._page += 1  # noqa: SLF001

        # fix the signature and annotations

        # the return value hint is complex to compute exactly from fct's return value
        # e.g. consider 'list[int] | str' should be transformed to 'Iterator[int | str]'
        # so we are just using 'Iterator[Any]'

        # see https://github.com/python/mypy/issues/12472 for ignore below
        wrapped.__signature__ = sig.replace(  # type: ignore[attr-defined]
            parameters=parameters[:param_pos] + parameters[param_pos + 1 :],
            return_annotation=Iterator[Any],
        )

        with suppress(KeyError):  # maybe no type hint
            del wrapped.__annotations__["pagination"]
        wrapped.__annotations__["return"] = Iterator[Any]

        return wrapped

    # see https://github.com/python/mypy/issues/15065 for the ignore below
    return paginated_decorator  # type: ignore[return-value]
