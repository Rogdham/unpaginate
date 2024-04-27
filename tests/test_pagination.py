import sys
from typing import Callable, Optional

import pytest

from unpaginate import Pagination

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import assert_type
else:  # pragma: no cover
    from typing import assert_type


def test_pagination_is_last_page_read_write() -> None:
    pagination = Pagination(page=13, offset=37, context=None)
    assert pagination.is_last_page is False

    pagination.is_last_page = True
    assert pagination.is_last_page is True


def test_pagination_context_readwrite() -> None:
    initial_context = object()
    pagination = Pagination(page=13, offset=37, context=initial_context)
    assert pagination.context == initial_context

    new_context = object()
    assert pagination.context != new_context
    pagination.context = new_context
    assert pagination.context == new_context


def test_pagination_attributes_readonly() -> None:
    pagination = Pagination(page=13, offset=37, context=None)
    assert pagination.page == 13
    assert pagination.offset == 37

    with pytest.raises(AttributeError):
        pagination.page = 42  # type: ignore[misc]
    with pytest.raises(AttributeError):
        pagination.offset = 37  # type: ignore[misc]


def test_pagination_typing() -> None:
    def set_pagination_context(pagination: Pagination[Optional[bytes]]) -> None:
        assert_type(pagination.context, Optional["bytes"])
        pagination.context = b"foo" + (pagination.context or b"")

    pagination0 = Pagination(page=13, offset=37, context=None)
    assert_type(pagination0, Pagination[None])
    assert_type(pagination0.context, None)
    assert pagination0.context is None
    set_pagination_context(pagination0)
    assert pagination0.context == b"foo"

    pagination1 = Pagination(page=13, offset=37, context=b"bar")
    assert_type(pagination1, Pagination[bytes])
    assert_type(pagination1.context, bytes)
    assert pagination1.context == b"bar"
    set_pagination_context(pagination1)
    assert pagination1.context == b"foobar"

    pagination2 = Pagination[Optional[bytes]](page=13, offset=37, context=None)
    assert_type(pagination2, Pagination[Optional[bytes]])
    assert_type(pagination2.context, Optional[bytes])
    assert pagination2.context is None
    set_pagination_context(pagination2)
    assert pagination2.context == b"foo"


def test_pagination_typing_default() -> None:
    def handle_pagination(pagination: Pagination, /) -> None:
        assert_type(pagination, Pagination[None])
        assert_type(pagination.context, None)

    assert_type(handle_pagination, Callable[[Pagination[None]], None])


def test_pagination_repr() -> None:
    pagination = Pagination[Optional[str]](page=13, offset=37, context=None)
    assert (
        str(pagination)
        == "Pagination(page=13, offset=37, is_last_page=False, context=None)"
    )

    pagination.context = "foobar"
    assert (
        str(pagination)
        == "Pagination(page=13, offset=37, is_last_page=False, context='foobar')"
    )

    pagination.is_last_page = True
    assert (
        str(pagination)
        == "Pagination(page=13, offset=37, is_last_page=True, context='foobar')"
    )
