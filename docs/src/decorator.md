# The `unpaginate` decorator

Assuming you have a function that returns (or yields) one page of items, the following
changes must be performed to use the _Unpaginate_ library:

- Decorate the function with `@unpaginate(...)`
- Add a `pagination` parameter **as first parameter** of the decorated function
- Use some [attributes of `pagination`](pagination.md) in the code to get the right
  items of the current page

!!! Tip

    If you decorate a class method instead of a function, the `pagination` parameter
    must be the second parameter instead, just after `self`.

!!! Note

    The `pagination` parameter is called by position and not by name, so you can use the
    [`/` syntax][slash syntax] from [PEP 570] to reflect that. However, its name still
    needs to be called `pagination`.

[slash syntax]:
  https://docs.python.org/3/faq/programming.html#what-does-the-slash-in-the-parameter-list-of-a-function-mean
[PEP 570]: https://peps.python.org/pep-0570/

## Decorator parameters {id=parameters}

These parameters can be passed when decorating the function. For example, decorate with
`@unpaginate(page=1)` so that the index of the first page is `1`.

page (`int`)

: The initial value of [`pagination.page`](pagination.md#page). Defaults to `0`.

offset (`int`)

: The initial value of [`pagination.offset`](pagination.md#offset). Defaults to `0`.

context_factory (callable)

: This function is called with no arguments to create the initial value of
[`pagination.context`](pagination.md#context). If not present, the initial value is
`None`.

stop (callable)

: Allows to specify the [stop condition](stop.md). Defaults to
[`stop_when_empty`](stop.md#stop_when_empty).

## Short form {id=short}

It is possible to decorate with `@unpaginate` as a shortcut for `@unpaginate()`.
