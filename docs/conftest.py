import sys
from typing import Dict, Optional

import pytest

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Iterable
else:  # pragma: no cover
    from collections.abc import Iterable


@pytest.fixture(scope="module", autouse=True)
def _import_pytest(doctest_namespace: Dict[str, object]) -> None:
    doctest_namespace["Iterable"] = Iterable
    doctest_namespace["Optional"] = Optional
