<div class="home-header" markdown="1">

# Unpaginate

<div class="description">Chain calls of paginated APIs</div>

</div>

## Introduction

<!-- BEGIN README INSERT -->

API endpoints are often paginated, meaning that you must chain requests to get the
content in full. _Unpaginate_ provides a decorator to make that task easy:

    :::python
    >>> from unpaginate import unpaginate

    >>> @unpaginate
    ... def get_cities(pagination, country):
    ...     return requests.post(
    ...         "https://api.example.org/cities",
    ...         json={"country": country, "page": pagination.page},
    ...     ).json()["items"]

Calling the decorated function allows to iterate over all items of all pages:

    :::python
    >>> iterator = get_cities("France")  # the 'pagination' parameter is added by the decorator
    >>> iterator
    <generator object get_cities ...>

    >>> next(iterator)
    'Paris'
    >>> next(iterator)
    'Lyon'
    >>> next(iterator)
    'Marseille'

All pagination schemes are supported:

- [By page index](usecases.md#by-page)
- [By offset](usecases.md#by-offset)
- [Using a cursor](usecases.md#by-cursor)
- Other schemes through [avdanced mode](usecases.md#advanced)

<!-- END README INSERT -->

!!! Tip

    It's not just API calls! All functions can be decorated with `unpaginate`!

    The `requests` module is used for illustrative purposes only.

## Installation

Install _Unpaginate_ with pip:

    :::sh
    $ python -m pip install unpaginate

## Python version support

As a general rule, all Python versions that are both [released and still officially
supported][python-versions] are supported by `unpaginate` and tested against.

If you have other use cases or find issues with some Python versions, feel free to
[open a ticket](https://github.com/Rogdham/unpaginate/issues/new)!

[python-versions]: https://devguide.python.org/versions/#supported-versions

## Status of the project

_Unpaginate_ is currently in **alpha**: the API may change in future releases. Changes
are well detailed in the [changelog], and the version numbering follow [semver].

[changelog]: https://github.com/Rogdham/unpaginate/blob/master/CHANGELOG.md
[semver]: https://semver.org/
