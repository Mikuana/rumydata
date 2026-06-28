import tempfile
from pathlib import Path

import pytest

from rumydata.field import Choice
from rumydata.field import Date
from rumydata.field import Integer
from rumydata.field import Text


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
