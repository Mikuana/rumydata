import pytest

from rumydata import table, Layout, field
from rumydata.rules import row as rr, header as hr
from tests.utils import file_row_harness


def test_row_good(basic):
    row = ['1', '2', '2020-01-01', 'X']
    assert not Layout(basic).check_row(row)
    assert not file_row_harness(row, basic)


def test_row_choice(basic):
    fields = {'c1': field.Choice(['x'], nullable=True)}
    lay = Layout(fields)
    assert not lay.check_row(['x'])
    assert not lay.check_row([''])
    assert not file_row_harness(['x'], fields)
    assert not file_row_harness([''], fields)


@pytest.mark.parametrize('value,err', [
    ([1, 2, 3, 4, 5], rr.RowLengthLTE),
    ([1, 2, 3], rr.RowLengthGTE)
])
def test_row_bad(basic, value, err):
    assert table.Layout(basic)._has_error(value, err.rule_exception(), rule_type=rr.Rule)
    with pytest.raises(AssertionError):
        file_row_harness(value, basic)


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
