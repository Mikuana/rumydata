"""
This is a giant dumpster fire. It needs to be broken apart into a set of more
sensible scripts.
"""

import csv
import tempfile
import uuid
from datetime import datetime as dt
from pathlib import Path

import pytest

import rumydata.cell.rule
from rumydata import cell
from rumydata import exception as ex
from rumydata.base import CellData, Columns
from rumydata.cell import Cell
from rumydata.file import File
from rumydata.header import Header
from rumydata.row import Row


@pytest.fixture()
def basic() -> dict:
    return {'col1': cell.Text(1), 'col2': cell.Integer(1), 'col3': cell.Date()}


@pytest.fixture()
def minimal_layout():
    return Columns(dict(x=cell.Digit(1)))


@pytest.fixture()
def tmpdir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


def write_row(directory, columns: Columns, row):
    p = Path(directory, str(uuid.uuid4()))
    with p.open('w') as o:
        writer = csv.writer(o)
        writer.writerow(list(columns.definition))
        writer.writerow(row)
    return p


@pytest.fixture()
def basic_good(tmpdir):
    p = Path(tmpdir, 'good.csv')
    with p.open('w') as o:
        writer = csv.writer(o)
        writer.writerow(['col1', 'col2', 'col3'])
        writer.writerow(['A', '1', '2020-01-01'])
    yield p.as_posix()


@pytest.fixture()
def readme_layout():
    return {
        'col1': cell.Text(8),
        'col2': cell.Choice(['x', 'y', 'z'], nullable=True),
        'col3': cell.Integer(1)
    }


@pytest.fixture()
def readme_data(tmpdir):
    p = Path(tmpdir, 'bobs_data.csv')
    p.write_text('\n'.join([
        "col1,col2,col3",
        "abc,x,-1",
        "def,,0",
        "ghi,a,1"
    ]))
    yield p.as_posix()


def minimal_bad(rows, directory):
    p = Path(directory, str(uuid.uuid4()))
    with p.open('w') as f:
        w = csv.writer(f)
        w.writerow(['x'])
        for i in range(rows):
            w.writerow(['12'])
    return p


def test_file_not_exists(basic):
    assert File(Columns(basic)).has_error('abc123.csv', FileNotFoundError)


@pytest.mark.parametrize('value,kwargs', [
    ('x', dict(max_length=1)),
    ('x', dict(max_length=2)),
    ('', dict(max_length=1, nullable=True)),
    ('', dict(max_length=1, min_length=1, nullable=True))
])
def test_text_good(value, kwargs):
    assert not cell.Text(**kwargs).check(CellData(value))


@pytest.mark.parametrize('value,kwargs,err', [
    ('', dict(max_length=1), ex.NullValueError),
    ('xxx', dict(max_length=2), ex.LengthError),
    ('x', dict(max_length=80, min_length=2), ex.LengthError),
])
def test_text_bad(value, kwargs, err):
    assert cell.Text(**kwargs).has_error(CellData(value), err)


@pytest.mark.parametrize('value,kwargs', [
    ('2020-01-01', {}),
    ('', dict(nullable=True)),
    ('2020-01-01', dict(max_date='2020-01-01')),
    ('2020-01-01', dict(max_date='2020-01-02')),
    ('2020-01-01', dict(min_date='2020-01-01', max_date='2020-01-02'))
])
def test_date_good(value, kwargs):
    assert not cell.Date(**kwargs).check(CellData(value))


@pytest.mark.parametrize('value,err,kwargs', [
    ('', ex.NullValueError, {}),
    ('20200101', ex.ConversionError, {}),
    ('9999-99-99', ex.ConversionError, {}),
    ('2020-01-01', ex.ValueComparisonError, dict(min_date='2020-01-02')),
    ('2020-01-02', ex.ValueComparisonError, dict(max_date='2020-01-01')),
    ('2020-01-01', ex.ValueComparisonError, dict(min_date='2020-01-02', max_date='2020-01-03')),
    ('2020-01-05', ex.ValueComparisonError, dict(min_date='2020-01-02', max_date='2020-01-03'))
])
def test_date_bad(value, err, kwargs):
    assert cell.Date(**kwargs).has_error(CellData(value), err)


@pytest.mark.parametrize('value,sig_dig,kwargs', [
    ('123.45', 5, {}),
    ('123.00', 5, {}),
    ('123.0', 5, {}),
    ('123', 5, {}),
    ('', 1, dict(nullable=True)),
    ('-0.01', 3, dict(rules=[cell.rule.NumericLT(0)])),
    ('0', 3, dict(rules=[cell.rule.NumericLTE(0)])),
    ('0.00', 3, dict(rules=[cell.rule.NumericET(0)])),
    ('0', 3, dict(rules=[cell.rule.NumericGTE(0)])),
    ('0.01', 3, dict(rules=[cell.rule.NumericGT(0)])),
])
def test_currency_good(value, sig_dig, kwargs):
    assert not cell.Currency(sig_dig, **kwargs).check(CellData(value))


@pytest.mark.parametrize('value,sig_dig,rules,err', [
    ('0.00', 5, [cell.rule.NumericLT(0)], ex.ValueComparisonError),
    ('0.01', 5, [cell.rule.NumericLTE(0)], ex.ValueComparisonError),
    ('0.01', 5, [cell.rule.NumericET(0)], ex.ValueComparisonError),
    ('-0.01', 5, [cell.rule.NumericGTE(0)], ex.ValueComparisonError),
    ('-0.01', 5, [cell.rule.NumericGT(0)], ex.ValueComparisonError),
    ('', 5, [], ex.NullValueError),
    ('123.45', 4, [], ex.LengthError),
    ('123.', 4, [], ex.CurrencyPatternError),
    ('123.456', 4, [], ex.CurrencyPatternError)
])
def test_currency_bad(value, sig_dig, rules, err):
    assert cell.Currency(sig_dig, rules=rules).has_error(CellData(value), err)


@pytest.mark.parametrize('value,max_length, kwargs', [
    ('1', 3, {}),
    ('12', 3, {}),
    ('123', 3, {}),
    ('12', 2, dict(min_length=2)),
    ('123', 3, dict(min_length=2))
])
def test_digit_good(value, max_length, kwargs):
    assert not cell.Digit(max_length, **kwargs).check(CellData(value))


@pytest.mark.parametrize('value,max_length,err,kwargs', [
    ('-123', 3, ex.CharacterError, {}),
    ('-123', 3, ex.LengthError, {}),
    ('1', 2, ex.LengthError, dict(min_length=2)),
    ('5', 3, ex.LengthError, dict(min_length=2))
])
def test_digit_bad(value, max_length, err, kwargs):
    assert cell.Digit(max_length, **kwargs).has_error(CellData(value), err)


@pytest.mark.parametrize('value,max_length,kwargs', [
    ('-1', 1, {}),
    ('0', 1, {}),
    ('1', 1, {}),
    ('1', 2, {}),
    ('11', 2, dict(min_length=2)),
    ('', 1, dict(nullable=True)),
    ('-1', 1, dict(rules=[cell.rule.NumericLT(0)])),
    ('-1', 1, dict(rules=[cell.rule.NumericLTE(0)])),
    ('0', 1, dict(rules=[cell.rule.NumericLTE(0)])),
    ('0', 1, dict(rules=[cell.rule.NumericET(0)])),
    ('0', 1, dict(rules=[cell.rule.NumericGTE(0)])),
    ('1', 1, dict(rules=[cell.rule.NumericGTE(0)])),
    ('1', 1, dict(rules=[cell.rule.NumericGT(0)]))
])
def test_integer_good(value, max_length, kwargs):
    assert not cell.Integer(max_length, **kwargs).check(CellData(value))


@pytest.mark.parametrize('value,max_length,kwargs,err', [
    ('0', 1, dict(rules=[cell.rule.NumericLT(0)]), ex.ValueComparisonError),
    ('1', 1, dict(rules=[cell.rule.NumericLTE(0)]), ex.ValueComparisonError),
    ('1', 1, dict(rules=[cell.rule.NumericET(0)]), ex.ValueComparisonError),
    ('-1', 1, dict(rules=[cell.rule.NumericGTE(0)]), ex.ValueComparisonError),
    ('0', 1, dict(rules=[cell.rule.NumericGT(0)]), ex.ValueComparisonError),
    ('', 1, {}, ex.NullValueError),
    ('1', 2, dict(min_length=2), ex.LengthError),
    ('111', 2, {}, ex.LengthError),
    ('00', 2, {}, ex.LeadingZeroError),
    ('01', 2, {}, ex.LeadingZeroError)
])
def test_integer_bad(value, max_length, kwargs, err):
    assert cell.Integer(max_length, **kwargs).has_error(CellData(value), err)


@pytest.mark.parametrize('value,choices,kwargs', [
    ('x', ['x'], {}),
    ('x', ['x', 'y'], {}),
    ('y', ['x', 'y'], {}),
    ('', ['x'], dict(nullable=True))
])
def test_choice_good(value, choices, kwargs):
    assert not cell.Choice(choices, **kwargs).check(CellData(value))


@pytest.mark.parametrize('value,choices,kwargs,err', [
    ('', ['x'], {}, ex.NullValueError),
    ('x', ['z'], {}, ex.InvalidChoiceError)
])
def test_choice_bad(value, choices, kwargs, err):
    assert cell.Choice(choices, **kwargs).has_error(CellData(value), err)


def test_row_good(basic):
    assert not Row(Columns(basic)).check(['1', '2', '2020-01-01'])


@pytest.mark.parametrize('value,err', [
    ([1, 2, 3, 4], ex.RowLengthError),
    ([1, 2], ex.RowLengthError)
])
def test_row_bad(basic, value, err):
    assert Row(Columns(basic)).has_error(value, err)


def test_header_good(basic):
    assert not Header(Columns(basic)).check(['col1', 'col2', 'col3'])


@pytest.mark.parametrize('value,err', [
    (['col1', 'col2'], ex.MissingColumnError),
    (['col1', 'col2', 'col2'], ex.DuplicateColumnError),
    (['col1', 'col2', 'col4'], ex.UnexpectedColumnError)
])
def test_header_bad(basic, value, err):
    assert Header(Columns(basic)).has_error(value, err)


def test_file_good(basic_good, basic):
    assert not File(Columns(basic)).check(basic_good)


def test_layout_good(basic, basic_good):
    assert not File(Columns(basic)).check(basic_good)


def test_readme_example(readme_layout, readme_data):
    assert File(Columns(readme_layout)). \
        has_error(readme_data, ex.InvalidChoiceError)


@pytest.mark.parametrize('rows,max_errors', [
    (1, 0),
    (2, 1),
    (101, 100),
    (int(1e5), 100),
])
def test_has_max_error(minimal_layout, tmpdir, rows, max_errors):
    assert File(minimal_layout, max_errors=max_errors). \
        has_error(minimal_bad(rows, tmpdir), ex.MaxExceededError)


@pytest.mark.parametrize('rows,max_errors', [
    (1, 1),
    (99, 100),
    (100, 100),
    (100, int(1e5)),
])
def test_missing_max_error(minimal_layout, tmpdir, rows, max_errors):
    assert not File(minimal_layout, max_errors=max_errors). \
        has_error(minimal_bad(rows, tmpdir), ex.MaxExceededError)


@pytest.mark.parametrize('value,func,assertion', [
    ('2', lambda x: int(x) % 2 == 0, "must be an even number"),
    ('1', lambda x: int(x) % 2 == 1, "must be an odd number"),
    ('2020-01-01', lambda x: dt.fromisoformat(x), "must be an isodate"),
])
def test_static_rules_good(value, func, assertion):
    x = Cell(rules=[cell.rule.make_static_cell_rule(func, assertion)])
    assert not x.check(CellData(value))


@pytest.mark.parametrize('value,func,assertion,kwargs', [
    ('2', lambda x: int(x) % 2 == 1, "must be an even number", {}),
    ('1', lambda x: int(x) % 2 == 0, "must be an odd number", {}),
    ('2020-00-01', lambda x: dt.fromisoformat(x), "must be an isodate", {}),
    ('', lambda x: 1 / 0, "custom exception", dict(exception=ZeroDivisionError))
])
def test_static_rules_bad(value, func, assertion, kwargs):
    x = Cell(rules=[cell.rule.make_static_cell_rule(func, assertion, **kwargs)])
    assert x.has_error(CellData(value), kwargs.get('exception', ex.UrNotMyDataError))


def test_column_compare_rule_good():
    x = Cell(rules=[rumydata.cell.rule.GreaterThanColumn('x')])
    assert not x.check(CellData('1', {'x': '0'}))


def test_column_compare_rule_bad():
    x = Cell(rules=[rumydata.cell.rule.GreaterThanColumn('x')])
    assert x.has_error('1', compare={'x': '1'}, error=ex.ColumnComparisonError)


def test_column_compare_row_good():
    row = Row(Columns({
        'a': cell.Integer(1, rules=[rumydata.cell.rule.GreaterThanColumn('b')]),
        'b': cell.Integer(1)
    }))
    assert not row.check(['3', '2'])


@pytest.mark.parametrize('compare_rule,row', [
    (rumydata.cell.rule.GreaterThanColumn('x'), ['2', '3']),
])
def test_column_compare_file_good(tmpdir, compare_rule, row):
    cols = Columns({'x': Cell(), 'y': Cell(rules=[compare_rule])})
    assert not File(cols).check(write_row(tmpdir, cols, row))


@pytest.mark.parametrize('compare_rule,row', [
    (rumydata.cell.rule.GreaterThanColumn('x'), ['1', '1']),
])
def test_column_compare_file_bad(tmpdir, compare_rule, row):
    cols = Columns({'x': Cell(), 'y': Cell(rules=[compare_rule])})
    assert File(cols).has_error(write_row(tmpdir, cols, row), ex.ColumnComparisonError)
