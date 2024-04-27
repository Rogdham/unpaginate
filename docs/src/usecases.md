# Use cases

The various uses cases in this page showcase representative examples of common
pagination schemes.

In most cases you will also be interested to learn about:

- [Stop conditions](stop.md): specify when the iteration will stop without calling the
  following page
- [Values held by the `pagination` argument](pagination.md): values of the current page,
  item offset, arbitrary context, etc.
- [Parameters of the `@unpaginate` decorator](decorator.md): for example to be able to
  specify the initial values of the `pagination` attributes

## By page index {id=by-page}

The value of the current page is held in `pagination.page`:

    :::python
    >>> from unpaginate import unpaginate

    >>> @unpaginate(page=1)
    ... def get_cities0(pagination, country):
    ...     return requests.post(
    ...         "https://api.example.org/cities",
    ...         json={"country": country, "page": pagination.page},
    ...     ).json()["items"]

## By offset {id=by-offset}

The index of the first item of the current page is held in `pagination.offset`:

    :::python
    >>> from unpaginate import stop_on_page_smaller_than, unpaginate

    >>> @unpaginate(stop=stop_on_page_smaller_than(100))
    ... def get_cities1(pagination, country):
    ...     return requests.post(
    ...         "https://api.example.org/cities",
    ...         json={"country": country, "start": pagination.offset, "limit": 100},
    ...     ).json()["items"]

## Using a cursor {id=by-cursor}

Arbitrary data can be passed from one page to the other via `pagination.context`; this
is ideal for API responses containing a cursor to fetch the next page.

Get the cursor for the current page from the context, and write the cursor for the next
page:

    :::python
    >>> from unpaginate import stop_on_falsy_context, unpaginate

    >>> @unpaginate(stop=stop_on_falsy_context)
    ... def get_cities2(pagination, country):
    ...     data = requests.post(
    ...         "https://api.example.org/cities",
    ...         json={"country": country, "cursor": pagination.context},
    ...     ).json()
    ...     pagination.context = data.get("next_cursor")
    ...     return data["items"]

## Advanced usage {id=advanced}

The usages above are the more frequent ones. Others can be implemented manually by
combining some of the following building blocks:

- Getting the [page](pagination.md#page) and [item offset](pagination.md#offset) values
  through `pagination.page` and `pagination.offset` respectively
- Passing [arbitrary data](pagination.md#context) from one page to the other though the
  `pagination.context` attribute
- [Specifying manually when the last page is reached](pagination.md#is_last_page) by
  setting `pagination.is_last_page` to `True`, and
  [avoid stopping on the first empty page](stop.md#stop_manual) by using
  `@unpaginate(stop=stop_manual)`
