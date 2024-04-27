from itertools import product
import re
import sys
from typing import Any, cast

import pytest

from unpaginate._pagination import Pagination
from unpaginate._stop import (
    stop_manual,
    stop_on_falsy_context,
    stop_on_page_smaller_than,
    stop_on_same_context,
    stop_when_empty,
)

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Callable
else:  # pragma: no cover
    from collections.abc import Callable


@pytest.mark.parametrize(
    ["fct", "expected_repr"],
    [
        pytest.param(fct, expected_repr, id=expected_repr)
        for fct, expected_repr in [
            # single
            (stop_manual, "stop_manual"),
            (stop_on_falsy_context, "stop_on_falsy_context"),
            (stop_on_page_smaller_than(42), "stop_on_page_smaller_than(42)"),
            (stop_on_same_context, "stop_on_same_context"),
            (stop_when_empty, "stop_when_empty"),
            # combine 2
            (
                stop_on_falsy_context | stop_on_page_smaller_than(42),
                "(stop_on_falsy_context | stop_on_page_smaller_than(42))",
            ),
            (
                stop_on_falsy_context & stop_on_page_smaller_than(42),
                "(stop_on_falsy_context & stop_on_page_smaller_than(42))",
            ),
            (stop_manual | stop_on_falsy_context, "stop_on_falsy_context"),
            (stop_manual & stop_on_falsy_context, "stop_manual"),
            # combine 3
            (
                stop_on_falsy_context
                | stop_on_page_smaller_than(42)
                | stop_on_same_context,
                "(stop_on_falsy_context | stop_on_page_smaller_than(42) | stop_on_same_context)",
            ),
            (
                stop_on_falsy_context & stop_on_page_smaller_than(42)
                | stop_on_same_context,
                "((stop_on_falsy_context & stop_on_page_smaller_than(42)) | stop_on_same_context)",
            ),
        ]
    ],
)
def test_stop_repr(fct: Callable[..., Any], expected_repr: str) -> None:
    assert repr(fct) == expected_repr


def test_stop_manual() -> None:
    pagination_placeholder = cast(Pagination[Any], object())
    assert not stop_manual(pagination_placeholder, pagination_placeholder)


def test_stop_when_empty() -> None:
    pagination_offset10 = Pagination(page=0, offset=10, context=None)
    pagination_offset20 = Pagination(page=0, offset=20, context=None)
    assert not stop_when_empty(pagination_offset10, pagination_offset20)
    assert stop_when_empty(pagination_offset20, pagination_offset20)


def test_stop_on_page_smaller_than() -> None:
    pagination_offset10 = Pagination(page=0, offset=10, context=None)
    pagination_offset20 = Pagination(page=0, offset=20, context=None)
    pagination_offset30 = Pagination(page=0, offset=30, context=None)
    assert stop_on_page_smaller_than(15)(pagination_offset10, pagination_offset10)
    assert stop_on_page_smaller_than(15)(pagination_offset10, pagination_offset20)
    assert not stop_on_page_smaller_than(15)(pagination_offset10, pagination_offset30)


def test_stop_on_falsy_context() -> None:
    pagination_empty = Pagination(page=0, offset=0, context="")
    pagination_foo = Pagination(page=0, offset=0, context="foo")
    assert stop_on_falsy_context(pagination_empty, pagination_empty)
    assert not stop_on_falsy_context(pagination_empty, pagination_foo)
    assert stop_on_falsy_context(pagination_foo, pagination_empty)
    assert not stop_on_falsy_context(pagination_foo, pagination_foo)


def test_stop_on_same_context() -> None:
    pagination_empty = Pagination(page=0, offset=0, context="")
    pagination_foo = Pagination(page=0, offset=0, context="foo")
    assert stop_on_same_context(pagination_empty, pagination_empty)
    assert not stop_on_same_context(pagination_empty, pagination_foo)
    assert not stop_on_same_context(pagination_foo, pagination_empty)
    assert stop_on_same_context(pagination_foo, pagination_foo)


def test_stop_combine_known_stop() -> None:
    stop_on_same_or_falsy_context = stop_on_same_context | stop_on_falsy_context
    stop_on_same_and_falsy_context = stop_on_same_context & stop_on_falsy_context

    pagination_empty = Pagination(page=0, offset=0, context="")
    pagination_foo = Pagination(page=0, offset=0, context="foo")
    pagination_bar = Pagination(page=0, offset=0, context="bar")

    for left, right in product(
        [pagination_empty, pagination_foo, pagination_bar], repeat=2
    ):
        same_context = stop_on_same_context(left, right)
        falsy_context = stop_on_falsy_context(left, right)
        assert stop_on_same_or_falsy_context(left, right) == (
            same_context or falsy_context
        ), f"{left=} {right=} {same_context=} {falsy_context=}"
        assert stop_on_same_and_falsy_context(left, right) == (
            same_context and falsy_context
        ), f"{left=} {right=} {same_context=} {falsy_context=}"


def test_stop_combine_with_stop_manual() -> None:
    stop_or = stop_manual | stop_on_falsy_context
    stop_and = stop_manual & stop_on_falsy_context

    pagination_empty = Pagination(page=0, offset=0, context="")
    pagination_foo = Pagination(page=0, offset=0, context="foo")

    for left, right in product([pagination_empty, pagination_foo], repeat=2):
        falsy_context = stop_on_falsy_context(left, right)
        assert stop_or(left, right) == (
            falsy_context
        ), f"{left=} {right=} {falsy_context=}"
        assert not stop_and(left, right), f"{left=} {right=} {falsy_context=}"


def test_stop_combine_custom_stop() -> None:
    def stop_custom(
        pagination_before: Pagination[Any],
        pagination_after: Pagination[Any],
        /,
    ) -> bool:
        return pagination_before.offset + pagination_after.offset == 20

    stop_or_custom = stop_on_same_context | stop_custom
    stop_ror_custom = stop_custom | stop_on_same_context
    stop_and_custom = stop_on_same_context & stop_custom
    stop_rand_custom = stop_custom & stop_on_same_context

    assert re.match(
        r"^\(stop_on_same_context \| <function.*stop_custom.*\)$",
        repr(stop_or_custom),
    )
    assert re.match(
        r"^\(<function.*stop_custom.* \| stop_on_same_context\)$",
        repr(stop_ror_custom),
    )
    assert re.match(
        r"^\(stop_on_same_context \& <function.*stop_custom.*\)$",
        repr(stop_and_custom),
    )
    assert re.match(
        r"^\(<function.*stop_custom.* \& stop_on_same_context\)$",
        repr(stop_rand_custom),
    )

    pagination0 = Pagination(page=0, offset=5, context="")
    pagination1 = Pagination(page=0, offset=10, context="foo")
    pagination2 = Pagination(page=0, offset=15, context="foo")

    for left, right in product([pagination0, pagination1, pagination2], repeat=2):
        same_context = stop_on_same_context(left, right)
        custom = stop_custom(left, right)
        assert stop_or_custom(left, right) == (
            same_context or custom
        ), f"{left=} {right=} {same_context=} {custom=}"
        assert stop_ror_custom(left, right) == (
            same_context or custom
        ), f"{left=} {right=} {same_context=} {custom=}"
        assert stop_and_custom(left, right) == (
            same_context and custom
        ), f"{left=} {right=} {same_context=} {custom=}"
        assert stop_rand_custom(left, right) == (
            same_context and custom
        ), f"{left=} {right=} {same_context=} {custom=}"


def test_stop_combine_custom_stop_invalid_type() -> None:
    with pytest.raises(TypeError):
        stop_on_same_context | 42  # type: ignore[operator]

    with pytest.raises(TypeError):
        42 | stop_on_same_context  # type: ignore[operator]

    with pytest.raises(TypeError):
        stop_on_same_context & 42  # type: ignore[operator]

    with pytest.raises(TypeError):
        42 & stop_on_same_context  # type: ignore[operator]
