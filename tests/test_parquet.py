from datetime import date
from pathlib import Path

import pandas as pd
import pytest

import rumydata.rules.cell
import rumydata.table
from rumydata import field
from rumydata.table import ParquetFile
from tests.utils import mock_no_module


@pytest.fixture()
def basic_good(tmpdir):
    p = Path(tmpdir, 'good.parquet')
    df = pd.DataFrame({
        'col1': ['A'],
        'col2': [1],
        'col3': [date(2020, 1, 1)],
        'col4': ['Z']
    })
    df.to_parquet(p)
    yield p.as_posix()


@pytest.fixture()
def basic_bad(tmpdir):
    p = Path(tmpdir, 'good.parquet')
    df = pd.DataFrame({
        'col1': ['A'],
        'col2': [1],
        'col3': [date(2020, 1, 1)],
        'col4': ['z']
    })
    df.to_parquet(p)
    yield p.as_posix()


def test_file_good(basic_good, basic):
    assert not ParquetFile(rumydata.table.Layout(basic)).check(basic_good)


def test_file_bad(basic_bad, basic):
    assert ParquetFile(rumydata.table.Layout(basic))._has_error(basic_bad, rumydata.rules.cell.Choice.rule_exception())


def test_no_pandas(mocker):
    mocker.patch('builtins.__import__', wraps=__import__, side_effect=mock_no_module('pandas'))
    with pytest.raises(ModuleNotFoundError):
        ParquetFile(rumydata.table.Layout({'x': field.Integer(1)}))


def test_no_pyarrow(mocker):
    mocker.patch('builtins.__import__', wraps=__import__, side_effect=mock_no_module('pyarrow'))
    with pytest.raises(ModuleNotFoundError):
        ParquetFile(rumydata.table.Layout({'x': field.Integer(1)}))
