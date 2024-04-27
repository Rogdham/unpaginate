from binascii import crc32
import sys
from typing import List, Optional, cast
from unittest.mock import Mock, call

from unpaginate import (
    Pagination,
    stop_manual,
    stop_on_falsy_context,
    stop_on_page_smaller_than,
    stop_on_same_context,
    stop_when_empty,
    unpaginate,
)

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Iterable
else:  # pragma: no cover
    from collections.abc import Iterable


def test_unpaginate_param_page() -> None:
    mock_range = Mock(side_effect=range)

    @unpaginate(page=42)
    def fct(pagination: Pagination) -> Iterable[int]:
        page_size = 20
        start = pagination.page * page_size
        stop = start + page_size
        if stop == 900:
            pagination.is_last_page = True
        return cast(range, mock_range(start, stop))

    assert list(fct()) == list(range(840, 900))
    assert mock_range.call_args_list == [
        call(840, 860),
        call(860, 880),
        call(880, 900),
    ]


def test_unpaginate_offset() -> None:
    mock_range = Mock(side_effect=range)

    @unpaginate(offset=42)
    def fct(pagination: Pagination) -> Iterable[int]:
        start = pagination.offset
        stop = start * 2 + 1
        if stop > 200:
            pagination.is_last_page = True
        return cast(range, mock_range(start, stop))

    assert list(fct()) == list(range(42, 343))
    assert mock_range.call_args_list == [
        call(42, 85),
        call(85, 171),
        call(171, 343),
    ]


def test_unpaginate_param_context_factory() -> None:
    def _init() -> bytes:
        return bytes.fromhex("00000000")

    @unpaginate(context_factory=_init)
    def fct(pagination: Pagination[bytes]) -> Iterable[str]:
        pagination.context = crc32(pagination.context).to_bytes(4, "big")
        value = pagination.context.hex()
        if value[0] == "0":
            pagination.is_last_page = True
        yield value

    assert list(fct()) == [
        "2144df1c",
        "5cf8b7c4",
        "2cc573b8",
        "9d6c8aba",
        "c57bfe72",
        "0c479aba",
    ]


def test_unpaginate_param_context_factory_multiple_calls() -> None:
    @unpaginate(context_factory=list)
    def fct(pagination: Pagination[List[int]], /) -> Iterable[str]:
        pagination.context.append(pagination.page)
        yield str(pagination.context)
        if pagination.page == 3:
            pagination.is_last_page = True

    assert list(fct()) == ["[0]", "[0, 1]", "[0, 1, 2]", "[0, 1, 2, 3]"]
    assert list(fct()) == ["[0]", "[0, 1]", "[0, 1, 2]", "[0, 1, 2, 3]"]
    assert list(fct()) == ["[0]", "[0, 1]", "[0, 1, 2]", "[0, 1, 2, 3]"]


def test_unpaginate_param_stop_manual() -> None:
    mock_range = Mock(side_effect=range)
    sizes = [30, 10, 20, 0, 40, 50]

    @unpaginate(stop=stop_manual)
    def fct(pagination: Pagination) -> Iterable[int]:
        start = pagination.offset
        try:
            stop = start + sizes[pagination.page]
        except IndexError:
            pagination.is_last_page = True
            return []
        return cast(range, mock_range(start, stop))

    assert list(fct()) == list(range(150))
    assert mock_range.call_args_list == [
        call(0, 30),
        call(30, 40),
        call(40, 60),
        call(60, 60),
        call(60, 100),
        call(100, 150),
    ]


def test_unpaginate_param_stop_when_empty() -> None:
    mock_range = Mock(side_effect=range)
    sizes = [30, 10, 20, 0, 40]

    @unpaginate(stop=stop_when_empty)
    def fct(pagination: Pagination) -> Iterable[int]:
        start = pagination.offset
        stop = start + sizes[pagination.page]
        return cast(range, mock_range(start, stop))

    assert list(fct()) == list(range(60))
    assert mock_range.call_args_list == [
        call(0, 30),
        call(30, 40),
        call(40, 60),
        call(60, 60),
    ]


def test_unpaginate_param_stop_on_page_smaller_than() -> None:
    mock_range = Mock(side_effect=range)
    sizes = [20, 30, 10, 40]

    @unpaginate(stop=stop_on_page_smaller_than(20))
    def fct(pagination: Pagination) -> Iterable[int]:
        start = pagination.offset
        stop = start + sizes[pagination.page]
        return cast(range, mock_range(start, stop))

    assert list(fct()) == list(range(60))
    assert mock_range.call_args_list == [
        call(0, 20),  # page size equal
        call(20, 50),  # page size greater than
        call(50, 60),  # page size lower than: stop after
    ]


def test_unpaginate_param_stop_on_falsy_context() -> None:
    contexts = ["a", "b", "c", "", "d"]

    @unpaginate(stop=stop_on_falsy_context)
    def fct(pagination: Pagination[Optional[str]]) -> Iterable[str]:
        yield f"context-{pagination.context}"
        pagination.context = contexts[pagination.page]

    assert list(fct()) == [
        "context-None",  # initial context being Falsy does not make it stop
        "context-a",
        "context-b",
        "context-c",
    ]


def test_unpaginate_param_stop_on_same_context() -> None:
    contexts = ["a", "b", "b", "c"]

    @unpaginate(stop=stop_on_same_context)
    def fct(pagination: Pagination[Optional[str]]) -> Iterable[str]:
        yield f"context-{pagination.context}"
        pagination.context = contexts[pagination.page]

    assert list(fct()) == [
        "context-None",  # initial context being Falsy does not make it stop
        "context-a",
        "context-b",
    ]


def test_unpaginate_all_params() -> None:
    def _init() -> bytes:
        return bytes.fromhex("00000000")

    @unpaginate(page=13, offset=37, context_factory=_init, stop=stop_manual)
    def fct(pagination: Pagination[bytes]) -> Iterable[str]:
        pagination.context = crc32(pagination.context).to_bytes(4, "big")
        value = pagination.context.hex()
        if value[0] == "6":
            pagination.is_last_page = True
        for _ in range(int(value[0], 16)):
            yield f"value={value} page={pagination.page} offset={pagination.offset}"

    assert list(fct()) == [
        # notice the following:
        #  - number of items is different per page
        #  - each offset increase by one with each item
        #  - a page is empty but it did not stop there
        "value=2144df1c page=13 offset=37",
        "value=2144df1c page=13 offset=38",
        "value=5cf8b7c4 page=14 offset=39",
        "value=5cf8b7c4 page=14 offset=40",
        "value=5cf8b7c4 page=14 offset=41",
        "value=5cf8b7c4 page=14 offset=42",
        "value=5cf8b7c4 page=14 offset=43",
        "value=2cc573b8 page=15 offset=44",
        "value=2cc573b8 page=15 offset=45",
        "value=9d6c8aba page=16 offset=46",
        "value=9d6c8aba page=16 offset=47",
        "value=9d6c8aba page=16 offset=48",
        "value=9d6c8aba page=16 offset=49",
        "value=9d6c8aba page=16 offset=50",
        "value=9d6c8aba page=16 offset=51",
        "value=9d6c8aba page=16 offset=52",
        "value=9d6c8aba page=16 offset=53",
        "value=9d6c8aba page=16 offset=54",
        "value=c57bfe72 page=17 offset=55",
        "value=c57bfe72 page=17 offset=56",
        "value=c57bfe72 page=17 offset=57",
        "value=c57bfe72 page=17 offset=58",
        "value=c57bfe72 page=17 offset=59",
        "value=c57bfe72 page=17 offset=60",
        "value=c57bfe72 page=17 offset=61",
        "value=c57bfe72 page=17 offset=62",
        "value=c57bfe72 page=17 offset=63",
        "value=c57bfe72 page=17 offset=64",
        "value=c57bfe72 page=17 offset=65",
        "value=c57bfe72 page=17 offset=66",
        # page 18 is missing because value 0c479aba starts with 0
        "value=be5dc3e3 page=19 offset=67",
        "value=be5dc3e3 page=19 offset=68",
        "value=be5dc3e3 page=19 offset=69",
        "value=be5dc3e3 page=19 offset=70",
        "value=be5dc3e3 page=19 offset=71",
        "value=be5dc3e3 page=19 offset=72",
        "value=be5dc3e3 page=19 offset=73",
        "value=be5dc3e3 page=19 offset=74",
        "value=be5dc3e3 page=19 offset=75",
        "value=be5dc3e3 page=19 offset=76",
        "value=be5dc3e3 page=19 offset=77",
        "value=61596c19 page=20 offset=78",
        "value=61596c19 page=20 offset=79",
        "value=61596c19 page=20 offset=80",
        "value=61596c19 page=20 offset=81",
        "value=61596c19 page=20 offset=82",
        "value=61596c19 page=20 offset=83",
    ]
