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
from openpyxl import Workbook

import rumydata.file
import rumydata.rules.cell
from rumydata import exception as ex
from rumydata import field
from rumydata.file import File
from rumydata.rules import header as hr, row as rr, column as cr


@pytest.fixture()
def basic() -> dict:
    return {'col1': rumydata.field.Text(1), 'col2': rumydata.field.Integer(1), 'col3': rumydata.field.Date()}


@pytest.fixture()
def minimal_layout():
    return rumydata.file.Layout(dict(x=rumydata.field.Digit(1)))


@pytest.fixture()
def tmpdir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


def write_row(directory, columns: rumydata.file.Layout, row, rows=False):
    p = Path(directory, str(uuid.uuid4()))
    with p.open('w', newline='') as o:
        writer = csv.writer(o)
        writer.writerow(list(columns.definition))
        if rows:
            for r in row:
                writer.writerow(r)
        else:
            writer.writerow(row)
    return p


@pytest.fixture()
def basic_good(tmpdir):
    p = Path(tmpdir, 'good.csv')
    with p.open('w', newline='') as o:
        writer = csv.writer(o)
        writer.writerow(['col1', 'col2', 'col3'])
        writer.writerow(['A', '1', '2020-01-01'])
    yield p.as_posix()


@pytest.fixture()
def basic_good_excel(tmpdir):
    p = Path(tmpdir, 'good.xlsx')
    wb = Workbook()
    ws = wb.active
    ws.append(['col1', 'col2', 'col3'])
    ws.append(['A', '1', '2020-01-01'])
    wb.save(p)
    yield p.as_posix()


@pytest.fixture()
def basic_row_skip_good(tmpdir):
    p = Path(tmpdir, 'good.csv')
    with p.open('w', newline='') as o:
        writer = csv.writer(o)
        writer.writerow(['garbage'])
        writer.writerow(['garbage'])
        writer.writerow(['col1', 'col2', 'col3'])
        writer.writerow(['A', '1', '2020-01-01'])
    yield p.as_posix()


@pytest.fixture()
def readme_layout():
    return {
        'col1': field.Text(8),
        'col2': field.Choice(['x', 'y', 'z'], nullable=True),
        'col3': field.Integer(1)
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


def empty_rows(rows, directory):
    p = Path(directory, str(uuid.uuid4()))
    with p.open('w') as f:
        w = csv.writer(f)
        w.writerow(['x'])
        for i in range(rows):
            w.writerow('')
    return p


def test_file_not_exists(basic):
    assert File(rumydata.file.Layout(basic)).__has_error__('abc123.csv', FileNotFoundError)


@pytest.mark.parametrize('value,kwargs', [
    ('x', dict(max_length=1)),
    ('x', dict(max_length=2)),
    ('', dict(max_length=1, nullable=True)),
    ('', dict(max_length=1, min_length=1, nullable=True))
])
def test_text_good(value, kwargs):
    assert not rumydata.field.Text(**kwargs).check_cell(value)


@pytest.mark.parametrize('value,kwargs,err', [
    ('', dict(max_length=1), ex.NullValueError),
    ('xxx', dict(max_length=2), ex.LengthError),
    ('x', dict(max_length=80, min_length=2), ex.LengthError),
])
def test_text_bad(value, kwargs, err):
    assert rumydata.field.Text(**kwargs).__has_error__(value, err)


@pytest.mark.parametrize('value,kwargs', [
    ('2020-01-01', {}),
    ('', dict(nullable=True)),
    ('2020-01-01', dict(max_date='2020-01-01')),
    ('2020-01-01', dict(max_date='2020-01-02')),
    ('2020-01-01', dict(min_date='2020-01-01', max_date='2020-01-02')),
    ('2020-01-01 00:00:00', dict(truncate_time=True))
])
def test_date_good(value, kwargs):
    assert not field.Date(**kwargs).check_cell(value)


@pytest.mark.parametrize('value,err,kwargs', [
    ('', ex.NullValueError, {}),
    ('20200101', ex.ConversionError, {}),
    ('9999-99-99', ex.ConversionError, {}),
    ('2020-01-01', ex.ValueComparisonError, dict(min_date='2020-01-02')),
    ('2020-01-02', ex.ValueComparisonError, dict(max_date='2020-01-01')),
    ('2020-01-01', ex.ValueComparisonError, dict(min_date='2020-01-02', max_date='2020-01-03')),
    ('2020-01-05', ex.ValueComparisonError, dict(min_date='2020-01-02', max_date='2020-01-03')),
    ('2020-01-01 00:00:00', ex.ConversionError, dict(truncate_time=True)),
    ('2020-01-01 00:00:01', ex.ConversionError, dict(truncate_time=False))
])
def test_date_bad(value, err, kwargs):
    assert rumydata.field.Date(**kwargs).__has_error__(value, err)


@pytest.mark.parametrize('value,sig_dig,kwargs', [
    ('123.45', 5, {}),
    ('123.00', 5, {}),
    ('123.0', 5, {}),
    ('123', 5, {}),
    ('', 1, dict(nullable=True)),
    ('-0.01', 3, dict(rules=[rumydata.rules.cell.NumericLT(0)])),
    ('0', 3, dict(rules=[rumydata.rules.cell.NumericLTE(0)])),
    ('0.00', 3, dict(rules=[rumydata.rules.cell.NumericET(0)])),
    ('0', 3, dict(rules=[rumydata.rules.cell.NumericGTE(0)])),
    ('0.01', 3, dict(rules=[rumydata.rules.cell.NumericGT(0)])),
])
def test_currency_good(value, sig_dig, kwargs):
    assert not rumydata.field.Currency(sig_dig, **kwargs).check_cell(value)


@pytest.mark.parametrize('value,sig_dig,rules,err', [
    ('0.00', 5, [rumydata.rules.cell.NumericLT(0)], ex.ValueComparisonError),
    ('0.01', 5, [rumydata.rules.cell.NumericLTE(0)], ex.ValueComparisonError),
    ('0.01', 5, [rumydata.rules.cell.NumericET(0)], ex.ValueComparisonError),
    ('-0.01', 5, [rumydata.rules.cell.NumericGTE(0)], ex.ValueComparisonError),
    ('-0.01', 5, [rumydata.rules.cell.NumericGT(0)], ex.ValueComparisonError),
    ('', 5, [], ex.NullValueError),
    ('123.45', 4, [], ex.LengthError),
    ('123.', 4, [], ex.CurrencyPatternError),
    ('123.456', 4, [], ex.CurrencyPatternError)
])
def test_currency_bad(value, sig_dig, rules, err):
    assert rumydata.field.Currency(sig_dig, rules=rules).__has_error__(value, err)


@pytest.mark.parametrize('value,max_length, kwargs', [
    ('1', 3, {}),
    ('12', 3, {}),
    ('123', 3, {}),
    ('12', 2, dict(min_length=2)),
    ('123', 3, dict(min_length=2))
])
def test_digit_good(value, max_length, kwargs):
    assert not rumydata.field.Digit(max_length, **kwargs).check_cell(value)


@pytest.mark.parametrize('value,max_length,err,kwargs', [
    ('-123', 3, ex.CharacterError, {}),
    ('-123', 3, ex.LengthError, {}),
    ('1', 2, ex.LengthError, dict(min_length=2)),
    ('5', 3, ex.LengthError, dict(min_length=2))
])
def test_digit_bad(value, max_length, err, kwargs):
    assert rumydata.field.Digit(max_length, **kwargs).__has_error__(value, err)


@pytest.mark.parametrize('value,max_length,kwargs', [
    ('-1', 1, {}),
    ('0', 1, {}),
    ('1', 1, {}),
    ('1', 2, {}),
    ('11', 2, dict(min_length=2)),
    ('', 1, dict(nullable=True)),
    ('-1', 1, dict(rules=[rumydata.rules.cell.NumericLT(0)])),
    ('-1', 1, dict(rules=[rumydata.rules.cell.NumericLTE(0)])),
    ('0', 1, dict(rules=[rumydata.rules.cell.NumericLTE(0)])),
    ('0', 1, dict(rules=[rumydata.rules.cell.NumericET(0)])),
    ('0', 1, dict(rules=[rumydata.rules.cell.NumericGTE(0)])),
    ('1', 1, dict(rules=[rumydata.rules.cell.NumericGTE(0)])),
    ('1', 1, dict(rules=[rumydata.rules.cell.NumericGT(0)]))
])
def test_integer_good(value, max_length, kwargs):
    assert not rumydata.field.Integer(max_length, **kwargs).check_cell(value)


@pytest.mark.parametrize('value,max_length,kwargs,err', [
    ('0', 1, dict(rules=[rumydata.rules.cell.NumericLT(0)]), ex.ValueComparisonError),
    ('1', 1, dict(rules=[rumydata.rules.cell.NumericLTE(0)]), ex.ValueComparisonError),
    ('1', 1, dict(rules=[rumydata.rules.cell.NumericET(0)]), ex.ValueComparisonError),
    ('-1', 1, dict(rules=[rumydata.rules.cell.NumericGTE(0)]), ex.ValueComparisonError),
    ('0', 1, dict(rules=[rumydata.rules.cell.NumericGT(0)]), ex.ValueComparisonError),
    ('', 1, {}, ex.NullValueError),
    ('1', 2, dict(min_length=2), ex.LengthError),
    ('111', 2, {}, ex.LengthError),
    ('00', 2, {}, ex.LeadingZeroError),
    ('01', 2, {}, ex.LeadingZeroError)
])
def test_integer_bad(value, max_length, kwargs, err):
    assert rumydata.field.Integer(max_length, **kwargs).__has_error__(value, err)


@pytest.mark.parametrize('value,choices,kwargs', [
    ('x', ['x'], {}),
    ('x', ['x', 'y'], {}),
    ('y', ['x', 'y'], {}),
    ('', ['x'], dict(nullable=True)),
    ('X', ['x'], dict(case_insensitive=True)),
    ('x', ['X'], dict(case_insensitive=True))
])
def test_choice_good(value, choices, kwargs):
    assert not field.Choice(choices, **kwargs).check_cell(value)


@pytest.mark.parametrize('value,choices,kwargs,err', [
    ('', ['x'], {}, ex.NullValueError),
    ('x', ['z'], {}, ex.InvalidChoiceError)
])
def test_choice_bad(value, choices, kwargs, err):
    assert field.Choice(choices, **kwargs).__has_error__(value, err)


def test_row_good(basic):
    assert not rumydata.file.Layout(basic).check_row(['1', '2', '2020-01-01'])


@pytest.mark.parametrize('value,err', [
    ([1, 2, 3, 4], ex.RowLengthError),
    ([1, 2], ex.RowLengthError)
])
def test_row_bad(basic, value, err):
    assert rumydata.file.Layout(basic).__has_error__(value, err, rule_type=rr.Rule)


def test_header_good(basic):
    assert not rumydata.file.Layout(basic).check_header(['col1', 'col2', 'col3'])


@pytest.mark.parametrize('value,err', [
    (['col1', 'col2'], ex.MissingColumnError),
    (['col1', 'col2', 'col2'], ex.DuplicateColumnError),
    (['col1', 'col2', 'col4'], ex.UnexpectedColumnError)
])
def test_header_bad(basic, value, err):
    assert rumydata.file.Layout(basic).__has_error__(value, err, rule_type=hr.Rule)


def test_header_skip(basic):
    assert not rumydata.file.Layout(basic, skip_header=True).check_header(['col1', 'col2', 'col4'])


def test_file_good(basic_good, basic):
    assert not File(rumydata.file.Layout(basic)).check(basic_good)


def test_file_excel_good(basic_good_excel, basic):
    assert not File(rumydata.file.Layout(basic), file_type='excel').check(basic_good_excel)


def test_file_row_skip_good(basic_row_skip_good, basic):
    assert not File(rumydata.file.Layout(basic), skip_rows=2).check(basic_row_skip_good)


def test_layout_good(basic, basic_good):
    assert not File(rumydata.file.Layout(basic)).check(basic_good)


def test_readme_example(readme_layout, readme_data):
    assert File(rumydata.file.Layout(readme_layout)).__has_error__(readme_data, ex.InvalidChoiceError)


@pytest.mark.parametrize('rows,me', [
    (1, 0),
    (2, 1),
    (101, 100),
    (int(1e5), 100),
])
def test_has_max_error(tmpdir, rows, me):
    fields = rumydata.file.Layout({'x': field.Field()})
    file = empty_rows(rows, tmpdir)
    assert File(fields, max_errors=me).__has_error__(file, ex.MaxExceededError)


@pytest.mark.parametrize('rows,me', [
    (1, 1),
    (99, 100),
    (100, 100),
    (100, int(1e5)),
])
def test_missing_max_error(tmpdir, rows, me):
    fields = rumydata.file.Layout({'x': field.Field()})
    file = empty_rows(rows, tmpdir)
    assert not File(fields, max_errors=me).__has_error__(file, ex.MaxExceededError)


@pytest.mark.parametrize('value,func,assertion', [
    ('2', lambda x: int(x) % 2 == 0, "must be an even number"),
    ('1', lambda x: int(x) % 2 == 1, "must be an odd number"),
    ('2020-01-01', lambda x: dt.fromisoformat(x), "must be an isodate"),
])
def test_static_rules_good(value, func, assertion):
    x = field.Field(rules=[rumydata.rules.cell.make_static_cell_rule(func, assertion)])
    assert not x.check_cell(value)


@pytest.mark.parametrize('value,func,assertion,kwargs', [
    ('2', lambda x: int(x) % 2 == 1, "must be an even number", {}),
    ('1', lambda x: int(x) % 2 == 0, "must be an odd number", {}),
    ('2020-00-01', lambda x: dt.fromisoformat(x), "must be an isodate", {}),
    ('', lambda x: 1 / 0, "custom exception", dict(exception=ZeroDivisionError))
])
def test_static_rules_bad(value, func, assertion, kwargs):
    x = field.Field(rules=[rumydata.rules.cell.make_static_cell_rule(func, assertion, **kwargs)])
    assert x.__has_error__(value, kwargs.get('exception', ex.UrNotMyDataError))


def test_column_compare_rule_good():
    x = field.Field(rules=[rumydata.rules.cell.GreaterThanColumn('x')])
    assert not x.check_cell(('1', {'x': '0'}))


def test_column_compare_rule_bad():
    x = field.Field(rules=[rumydata.rules.cell.GreaterThanColumn('x')])
    assert x.__has_error__('1', compare={'x': '1'}, error=ex.ColumnComparisonError)


def test_column_compare_row_good():
    fields = rumydata.file.Layout({
        'a': rumydata.field.Integer(1, rules=[rumydata.rules.cell.GreaterThanColumn('b')]),
        'b': rumydata.field.Integer(1)
    })
    assert not fields.check_row(['3', '2'])


@pytest.mark.parametrize('compare_rule,row', [
    (rumydata.rules.cell.GreaterThanColumn('x'), ['2', '3']),
])
def test_column_compare_file_good(tmpdir, compare_rule, row):
    cols = rumydata.file.Layout({'x': field.Field(), 'y': field.Field(rules=[compare_rule])})
    assert not File(cols).check(write_row(tmpdir, cols, row))


@pytest.mark.parametrize('compare_rule,row', [
    (rumydata.rules.cell.GreaterThanColumn('x'), ['1', '1']),
])
def test_column_compare_file_bad(tmpdir, compare_rule, row):
    cols = rumydata.file.Layout({'x': field.Field(), 'y': field.Field(rules=[compare_rule])})
    assert File(cols).__has_error__(write_row(tmpdir, cols, row), ex.ColumnComparisonError)


def test_unique_bad(tmpdir):
    cols = rumydata.file.Layout({'x': field.Field(rules=[cr.Unique()])})
    f = write_row(tmpdir, cols, [['1'], ['1'], ['1']], rows=True)
    assert File(cols).__has_error__(f, ex.DuplicateValueError)


def test_unique_good(tmpdir):
    cols = rumydata.file.Layout({'x': field.Field(rules=[cr.Unique()])})
    f = write_row(tmpdir, cols, [['1'], ['2'], ['3']], rows=True)
    assert not File(cols).check(f)


@pytest.mark.parametrize('row,kwargs', [
    (['1', '1'], {}),
    (['1', '1'], dict(empty_row_ok=False)),
    (['', ''], dict(empty_row_ok=True))
])
def test_empty_row_good(row, kwargs):
    lay = rumydata.file.Layout({'x': field.Integer(1), 'y': field.Integer(2)}, **kwargs)
    assert not lay.check_row(row)


def test_empty_row_file_good(tmpdir):
    cols = rumydata.file.Layout({'x': field.Field()}, empty_row_ok=True)
    f = write_row(tmpdir, cols, [['1'], ['2'], ['']], rows=True)
    assert not File(cols).check(f)


@pytest.mark.parametrize('cell', [
    '',
    '1',
    '8k;asdfkl;asdf'
])
def test_ignore_cell(cell):
    assert not field.Ignore().check_cell(cell)


@pytest.mark.parametrize('row', [
    (['1', '']),
    (['', '']),
    (['1', '1'])
])
def test_ignore_row(row):
    """ Test that ignore rows count as empty for the purpose of accepting empty rows """
    lay = rumydata.file.Layout(
        {'x': field.Ignore(), 'y': field.Integer(1)}, empty_row_ok=True
    )
    assert not lay.check_row(row)
