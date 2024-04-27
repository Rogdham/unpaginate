# Pagination instance

The `Pagination` instance passed to the decorated functions as the argument `pagination`
contains the following attributes:

page (`int`, read-only) {id=page}

: The index of the current page.

offset (`int`, read-only) {id=offset}

: The index of the first item of the current page.

context {id=context}

: Arbitrary data. Used to pass data from one page to the other, or for
[stop conditions](stop.md).

is_last_page (`bool`) {id=is_last_page}

: Setting this attribute to `True` indicates that the current page is the last one, so
that the iteration is stopped and the next page is never called.
