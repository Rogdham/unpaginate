from contextlib import suppress
from copy import deepcopy
from functools import wraps
from inspect import Parameter, signature
import sys
from typing import Any, Final, Generic, Optional, Union, cast, overload

from unpaginate._pagination import Pagination
from unpaginate._stop import _CallableStop, stop_when_empty

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Callable, Iterable, Iterator
else:  # pragma: no cover
    from collections.abc import Callable, Iterable, Iterator

if sys.version_info < (3, 10):  # pragma: no cover
    from typing_extensions import Concatenate, ParamSpec

    NoneType = type(None)
else:  # pragma: no cover
    from types import NoneType
    from typing import Concatenate, ParamSpec

if sys.version_info < (3, 13):  # pragma: no cover
    from typing_extensions import TypeVar  # for 'default' parameter
else:  # pragma: no cover
    from typing import TypeVar


P = ParamSpec("P")
R = TypeVar("R")
S = TypeVar("S")
C_co = TypeVar("C_co", covariant=True, default=None)


# typing note: unpaginate can be applied on either functions or class methods
# for functions, the 'pagination' argument is expected to be the first parameter
# for methods, it is expected to be after the 'self' parameter
# a lot of the type complexity comes from supporting both cases

# note that as a side-effect, it works as well on functions
# where the 'pagination' argument is the second parameter


class _UnpaginateDecorator(Generic[C_co]):
    __slots__ = ["_page", "_offset", "_context_factory", "_stop"]

    def __init__(
        self,
        *,
        page: int,
        offset: int,
        context_factory: Callable[[], C_co],
        stop: _CallableStop[C_co],
    ) -> None:
        self._page: Final = page
        self._offset: Final = offset
        self._context_factory: Final = context_factory
        self._stop: Final = stop

    @overload  # pagination as first parameter
    def __call__(
        self, fct: Callable[Concatenate[Pagination[C_co], P], Iterable[R]], /
    ) -> Callable[P, Iterator[R]]: ...

    @overload  # pagination as second parameter
    def __call__(
        self, fct: Callable[Concatenate[S, Pagination[C_co], P], Iterable[R]], /
    ) -> Callable[Concatenate[S, P], Iterator[R]]: ...

    def __call__(
        self,
        fct: (
            Union[
                Callable[Concatenate[Pagination[C_co], P], Iterable[R]],
                Callable[Concatenate[S, Pagination[C_co], P], Iterable[R]],
            ]
        ),
        /,
    ) -> Union[
        Callable[P, Iterator[R]],
        Callable[Concatenate[S, P], Iterator[R]],
    ]:
        if isinstance(fct, (classmethod, staticmethod)):
            return type(fct)(self(fct.__func__))  # type: ignore[unreachable]

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
                f"Function '{fct.__name__}' to unpaginate "
                "must have 'pagination' as first parameter"
            )

        # create wrapped function

        @wraps(fct)  # type: ignore[arg-type]
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> Iterator[R]:
            pagination = Pagination(
                page=self._page,
                offset=self._offset,
                context=self._context_factory(),
            )

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
                        f"Function '{fct.__name__}' to unpaginate "
                        "cannot be called with a 'pagination' parameter"
                    ) from ex
                raise  # pragma: no cover
            arguments.apply_defaults()

            while not pagination.is_last_page:
                pagination_before = deepcopy(pagination)
                iterable = fct(*arguments.args, **arguments.kwargs)
                for item in iterable:
                    pagination._offset += 1  # noqa: SLF001
                    yield item
                if self._stop(pagination_before, pagination):
                    pagination.is_last_page = True
                pagination._page += 1  # noqa: SLF001

        # fix the signature and annotations

        # the return value hint is complex to compute exactly from fct's return value
        # e.g. consider 'list[int] | str' should be transformed to 'Iterator[int | str]'
        # so we are just using 'Iterator[Any]'
        return_annotation = Iterator[Any]

        # see https://github.com/python/mypy/issues/12472 for the ignore below
        wrapped.__signature__ = sig.replace(  # type: ignore[attr-defined]
            parameters=parameters[:param_pos] + parameters[param_pos + 1 :],
            return_annotation=return_annotation,
        )

        with suppress(KeyError):  # maybe no type hint
            del wrapped.__annotations__["pagination"]
        wrapped.__annotations__["return"] = return_annotation

        return wrapped


# the following defines the unpaginate decorator
# it can be called:
#  - in regular manner: '@unpaginate(...)'
#  - in short form '@unpaginate' as a shortcut for '@unpaginate()'


@overload  # '@unpaginate' shortcut with pagination as first parameter
def unpaginate(
    fct: Callable[Concatenate[Pagination[None], P], Iterable[R]], /
) -> Callable[P, Iterator[R]]: ...


@overload  # '@unpaginate' shortcut with pagination as second parameter
def unpaginate(
    fct: Callable[Concatenate[S, Pagination[None], P], Iterable[R]], /
) -> Callable[Concatenate[S, P], Iterator[R]]: ...


@overload  # regular '@unpaginate(...)' decorator
def unpaginate(
    *,
    page: int = ...,
    offset: int = ...,
    context_factory: Optional[Callable[[], C_co]] = ...,
    stop: _CallableStop[C_co] = ...,
) -> _UnpaginateDecorator[C_co]: ...


def unpaginate(
    fct: Union[
        Callable[Concatenate[Pagination[C_co], P], Iterable[R]],
        Callable[Concatenate[S, Pagination[C_co], P], Iterable[R]],
        None,
    ] = None,
    /,
    *,
    page: int = 0,
    offset: int = 0,
    context_factory: Optional[Callable[[], C_co]] = None,
    stop: _CallableStop[C_co] = stop_when_empty,
) -> Union[
    Callable[P, Iterator[R]],
    Callable[Concatenate[S, P], Iterator[R]],
    _UnpaginateDecorator[C_co],
]:
    decorator = _UnpaginateDecorator(
        page=page,
        offset=offset,
        context_factory=context_factory or cast(Callable[[], C_co], NoneType),
        stop=stop,
    )
    if fct is None:  # regular form '@unpaginate(...)'
        return decorator
    return decorator(fct)  # shortcut for '@unpaginate()'
