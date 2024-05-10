import tempfile
from pathlib import Path

import pytest
import sys
from rumydata.field import Text, Integer, Date, Choice


@pytest.fixture()
@pytest.mark.skipif(sys.version_info >= (3, 10))
def tmpdir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture()
@pytest.mark.skipif(sys.version_info < (3, 10))
def tmpdir():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        yield Path(d)

@pytest.fixture()
def basic() -> dict:
    return {
        'col1': Text(1),
        'col2': Integer(1),
        'col3': Date(),
        'col4': Choice(['X', 'Y', 'Z'])
    }
