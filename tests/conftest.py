import tempfile
from pathlib import Path

import pytest

from rumydata.field import Choice
from rumydata.field import Date
from rumydata.field import Integer
from rumydata.field import Text


def pytest_addoption(parser):
    parser.addoption(
        "--skipslow", action="store_true", default=False, help="skip slow tests"
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--skipslow"):
        return
    skip_slow = pytest.mark.skip(reason="skipped via --skipslow flag")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture()
def tmpdir():
    try:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)
    except PermissionError:
        pass

@pytest.fixture()
def basic() -> dict:
    return {
        'col1': Text(1),
        'col2': Integer(1),
        'col3': Date(),
        'col4': Choice(['X', 'Y', 'Z'])
    }
