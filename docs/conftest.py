import sys
from typing import Any, Dict, Optional, Union

import pytest

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Iterable
else:  # pragma: no cover
    from collections.abc import Iterable


class FakeResponse:
    def __init__(self, json: Any) -> None:  # noqa: ANN401
        self._json = json

    def json(self) -> Any:  # noqa: ANN401
        return self._json


class FakeRequests:
    @staticmethod
    def post(url: str, json: Dict[str, Union[str, int]]) -> FakeResponse:
        if url == "https://api.example.org/cities" and json["country"] == "France":
            if json["page"] == 0:
                return FakeResponse({"items": ["Paris", "Lyon"]})
            if json["page"] == 1:
                return FakeResponse({"items": ["Marseille"]})

        raise NotImplementedError("Fake requests for documentation", url, json)


@pytest.fixture(scope="module", autouse=True)
def _import_pytest(doctest_namespace: Dict[str, object]) -> None:
    doctest_namespace["Iterable"] = Iterable
    doctest_namespace["Optional"] = Optional
    doctest_namespace["requests"] = FakeRequests()
