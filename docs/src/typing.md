# Typing

_Unpaginate_ commes natively with type hints, which are checked by [_mypy_][mypy].

The benefits are twofold:

- Improve the correctness of the code of the library itself;
- Allow users of the library to benefit from well-defined type hints on the public API.

As a rule of thumbs, we follow [Postel's law][postels_law] by being as vague as possible
for the arguments of functions, and as precise as possible for the returned values.

[mypy]: https://mypy.readthedocs.io/en/stable/index.html
[postels_law]: https://en.wikipedia.org/wiki/Robustness_principle

## Pagination

The `pagination` parameter of the decorated functions can be annotated with
`Pagination`, or if the context is used with `Pagination[C]` (replacing `C` with the
type of the context):

    :::python
    >>> from unpaginate import Pagination, stop_on_falsy_context, unpaginate

    >>> @unpaginate(page=1)
    ... def get_cities0(pagination: Pagination, country: str) -> Iterable[str]:
    ...     return requests.post(
    ...         "https://api.example.org/cities",
    ...         json={"country": country, "page": pagination.page},
    ...     ).json()["items"]

<!---->

    :::python
    >>> @unpaginate(stop=stop_on_falsy_context)
    ... def get_cities2(pagination: Pagination[Optional[str]], country: str) -> Iterable[str]:
    ...     data = requests.post(
    ...         "https://api.example.org/cities",
    ...         json={"country": country, "cursor": pagination.context},
    ...     ).json()
    ...     pagination.context = data.get("next_cursor")
    ...     return data["items"]

!!! Tip

    In the second example, since no `context_factory` is specified, the initial value of
    the context is `None`. This is why the parameter of `Pagination` is `Optional[str]`
    and not simply `str`.

    This is not needed when a `context_factory` is specified:

        :::python
        @unpaginate(context_factory=str)
        def foo(pagination: Pagination[str]) -> Iterable[str]:
            raise NotImplementedError

!!! Note

    Depending on the configuration of the tool you use for validating type hints, you
    may need to use the [`/` syntax][slash syntax] from [PEP 570] to change the
    `pagination` parameter into a positional-only parameter, like so:

        :::python
        >>> @unpaginate(page=1)
        ... def get_cities1(pagination: Pagination, /, country: str) -> Iterable[str]:
        ...     ...

[slash syntax]:
  https://docs.python.org/3/faq/programming.html#what-does-the-slash-in-the-parameter-list-of-a-function-mean
[PEP 570]: https://peps.python.org/pep-0570/

## Stop

Annotate the two parameters of the stop callable with either `Pagination` or
`Pagination[C]` (same `C` value for both parameters):

    :::python
    >>> from unpaginate import Pagination

    >>> def my_stop_without_context(
    ...     pagination_before: Pagination,
    ...     pagination_after: Pagination,
    ... ) -> bool:
    ...     return pagination_before.offset * 2 > pagination_after.offset

<!---->

    :::python
    >>> def my_stop_with_context(
    ...     pagination_before: Pagination[int],
    ...     pagination_after: Pagination[int],
    ... ) -> bool:
    ...     return pagination_before.context + 1 != pagination_after.context
