import tempfile
from pathlib import Path

import pytest

from rumydata.field import Text, Integer, Date, Choice


@pytest.fixture()
def tmpdir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture()
def basic() -> dict:
    return {
        'col1': Text(1),
        'col2': Integer(1),
        'col3': Date(),
        'col4': Choice(['X', 'Y', 'Z'])
    }
