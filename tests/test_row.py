import pytest

from rumydata import table, field
from rumydata.rules import row as rr, header as hr


@pytest.fixture()
def basic() -> dict:
    return {
        'col1': field.Text(1),
        'col2': field.Integer(1),
        'col3': field.Date(),
        'col4': field.Choice(['X', 'Y', 'Z'])
    }


def test_row_good(basic):
    assert not table.Layout(basic).check_row(['1', '2', '2020-01-01', 'X'])


@pytest.mark.parametrize('value,err', [
    ([1, 2, 3, 4, 5], rr.RowLengthLTE),
    ([1, 2, 3], rr.RowLengthGTE)
])
def test_row_bad(basic, value, err):
    assert table.Layout(basic)._has_error(value, err.rule_exception(), rule_type=rr.Rule)


def test_header_good(basic):
    assert not table.Layout(basic).check_header(['col1', 'col2', 'col3', 'col4'])


@pytest.mark.parametrize('value,err', [
    (['col1', 'col2'], hr.NoMissing),
    (['col1', 'col2', 'col2'], hr.NoDuplicate),
    (['col1', 'col2', 'col5'], hr.NoExtra)
])
def test_header_bad(basic, value, err):
    assert table.Layout(basic)._has_error(value, err.rule_exception(), rule_type=hr.Rule)


def test_header_skip(basic):
    assert not table.Layout(basic, skip_header=True). \
        check_header(['col1', 'col2', 'col4'])


@pytest.mark.parametrize('row_length,row,expected', [
    (1, ['1', '2'], False),
    (1, ['1'], True)
])
def test_row_length_lte(row_length, row, expected):
    r = rr.RowLengthLTE(row_length)
    assert r._evaluator()(*r._prepare(row)) is expected


@pytest.mark.parametrize('row_length,row,expected', [
    (3, ['1', '2'], False),
    (2, ['1', '2'], True),
    (1, ['1', '2'], True)
])
def test_row_length_gte(row_length, row, expected):
    r = rr.RowLengthGTE(row_length)
    assert r._evaluator()(*r._prepare(row)) is expected
