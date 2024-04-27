# Stop conditions

By default, _Unpaginate_ chains pages together until one page has no items. This is the
default stop condition, which can be customized by specifying a callable to the `stop`
parameter of the decorator: `@unpaginate(stop=...)`.

## Provided stop conditions {id=provided}

    :::python
    >>> from unpaginate import (
    ...     stop_manual,
    ...     stop_on_falsy_context,
    ...     stop_on_page_smaller_than,
    ...     stop_on_same_context,
    ...     stop_when_empty,
    ... )

stop_manual {id=stop_manual}

: Never stops. Useful to override the default behavior when
[stopping manually with `pagination.is_last_page`](pagination.md#is_last_page).

stop_when_empty {id=stop_when_empty}

: Default behavior. Stops when a page has no items. Same behavior as
`stop_on_page_smaller_than(1)`.

stop_on_page_smaller_than(page_size) {id=stop_on_page_smaller_than}

: Stops when the number of items in the page is strictly lower than the number passed as
argument (e.g. `stop_on_page_smaller_than(100)` to stop when a page has 99 items or
less).

stop_on_falsy_context {id=stop_on_falsy_context}

: Stops when `bool(pagination.context)` is `False`.

stop_on_same_context {id=stop_on_same_context}

: Stops when `pagination.context` at the end of a page is equal to its value at the
beginning of the page.

## Combining stop conditions {id=combine}

Stops conditions can be combined with `|` and `&` operators.

For example, to stop when the context is falsy or equals to the one before the page,
use:

    :::python
    >>> from unpaginate import stop_on_falsy_context, stop_on_same_context, unpaginate

    >>> @unpaginate(stop=stop_on_falsy_context | stop_on_same_context)
    ... def fct(pagination):
    ...     ...

## Custom stop conditions {id=custom}

A stop condition is a callable that takes as parameters the `Pagination` instance at the
beginning of the page and at the end of the page, and returns a boolean indicating if
the iterations has to stop.

For example, to stop when the value on the context stops increasing by one:

    >>> def my_stop(pagination_before, pagination_after):
    ...     return pagination_before.context + 1 != pagination_after.context

!!! Tip

    The `|` and `&` operators will work as expected, assuming that one of the operands
    is a provided stop condition, e.g. `my_stop | stop_on_page_smaller_than(100)`.

    However, combining only custom stop conditions is not posible directly, instead
    start with `stop_manual` (because it does nothing): e.g.
    `stop_manual | my_stop1 | my_stop2`.
