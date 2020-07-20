import csv
import tempfile
import uuid
from datetime import datetime as dt
from pathlib import Path

import pytest

from rumydata.cell import *
from rumydata.exception import *
from rumydata.rule import make_static_rule
from rumydata.validation import File, Row, Header
from rumydata.validation import Layout, Cell


@pytest.fixture()
def basic() -> dict:
    return {'col1': Text(1), 'col2': Integer(1), 'col3': Date()}


@pytest.fixture()
def basic_definition(basic):
    return Layout(basic, pattern=r'good\.csv')


@pytest.fixture()
def minimal_layout():
    return Layout(dict(x=Digit(1)))


@pytest.fixture()
def tmpdir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


def write_row(directory, layout, row):
    p = Path(directory, str(uuid.uuid4()))
    with p.open('w') as o:
        writer = csv.writer(o)
        writer.writerow(list(layout.definition.keys()))
        writer.writerow(row)
    return p


@pytest.fixture()
def basic_good(tmpdir):
    p = Path(tmpdir, 'good.csv')
    with p.open('w') as o:
        writer = csv.writer(o)
        writer.writerow(['col1', 'col2', 'col3'])
        writer.writerow(['A', 1, '2020-01-01'])
    yield p.as_posix()


@pytest.fixture()
def readme_layout():
    return {
        'col1': Text(8),
        'col2': Choice(['x', 'y', 'z'], nullable=True),
        'col3': Integer(1)
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
    assert File(Layout(basic)).has_error('abc123.csv', FileNotFoundError)


@pytest.mark.parametrize('value,kwargs', [
    ('x', dict(max_length=1)),
    ('x', dict(max_length=2)),
    ('', dict(max_length=1, nullable=True)),
    ('', dict(max_length=1, min_length=1, nullable=True))
])
def test_text_good(value, kwargs):
    assert not Text(**kwargs).check(value)


@pytest.mark.parametrize('value,kwargs,err', [
    ('', dict(max_length=1), NullValueError),
    ('xxx', dict(max_length=2), LengthError),
    ('x', dict(max_length=80, min_length=2), LengthError),
])
def test_text_bad(value, kwargs, err):
    assert Text(**kwargs).has_error(value, err)


@pytest.mark.parametrize('value,kwargs', [
    ('2020-01-01', {}),
    ('', dict(nullable=True)),
    ('2020-01-01', dict(max_date='2020-01-01')),
    ('2020-01-01', dict(max_date='2020-01-02')),
    ('2020-01-01', dict(min_date='2020-01-01', max_date='2020-01-02'))
])
def test_date_good(value, kwargs):
    assert not Date(**kwargs).check(value)


@pytest.mark.parametrize('value,err,kwargs', [
    ('', NullValueError, {}),
    ('20200101', ConversionError, {}),
    ('9999-99-99', ConversionError, {}),
    ('2020-01-01', ValueComparisonError, dict(min_date='2020-01-02')),
    ('2020-01-02', ValueComparisonError, dict(max_date='2020-01-01')),
    ('2020-01-01', ValueComparisonError, dict(min_date='2020-01-02', max_date='2020-01-03')),
    ('2020-01-05', ValueComparisonError, dict(min_date='2020-01-02', max_date='2020-01-03'))
])
def test_date_bad(value, err, kwargs):
    assert Date(**kwargs).has_error(value, err)


@pytest.mark.parametrize('value,sig_dig,kwargs', [
    ('123.45', 5, {}),
    ('123.00', 5, {}),
    ('123.0', 5, {}),
    ('123', 5, {}),
    ('', 1, dict(nullable=True)),
    ('-0.01', 3, dict(rules=[rule.NumericLT(0)])),
    ('0', 3, dict(rules=[rule.NumericLTE(0)])),
    ('0.00', 3, dict(rules=[rule.NumericET(0)])),
    ('0', 3, dict(rules=[rule.NumericGTE(0)])),
    ('0.01', 3, dict(rules=[rule.NumericGT(0)])),
])
def test_currency_good(value, sig_dig, kwargs):
    assert not Currency(sig_dig, **kwargs).check(value)


@pytest.mark.parametrize('value,sig_dig,rules,err', [
    ('0.00', 5, [rule.NumericLT(0)], ValueComparisonError),
    ('0.01', 5, [rule.NumericLTE(0)], ValueComparisonError),
    ('0.01', 5, [rule.NumericET(0)], ValueComparisonError),
    ('-0.01', 5, [rule.NumericGTE(0)], ValueComparisonError),
    ('-0.01', 5, [rule.NumericGT(0)], ValueComparisonError),
    ('', 5, [], NullValueError),
    ('123.45', 4, [], LengthError),
    ('123.', 4, [], CurrencyPatternError),
    ('123.456', 4, [], CurrencyPatternError)
])
def test_currency_bad(value, sig_dig, rules, err):
    assert Currency(sig_dig, rules=rules).has_error(value, err)


@pytest.mark.parametrize('value,max_length, kwargs', [
    ('1', 3, {}),
    ('12', 3, {}),
    ('123', 3, {}),
    ('12', 2, dict(min_length=2)),
    ('123', 3, dict(min_length=2))
])
def test_digit_good(value, max_length, kwargs):
    assert not Digit(max_length, **kwargs).check(value)


@pytest.mark.parametrize('value,max_length,err,kwargs', [
    ('-123', 3, DataError, {}),
    ('-123', 3, LengthError, {}),
    ('1', 2, LengthError, dict(min_length=2)),
    ('5', 3, LengthError, dict(min_length=2))
])
def test_digit_bad(value, max_length, err, kwargs):
    assert Digit(max_length, **kwargs).has_error(value, err)


@pytest.mark.parametrize('value,max_length,kwargs', [
    ('-1', 1, {}),
    ('0', 1, {}),
    ('1', 1, {}),
    ('1', 2, {}),
    ('11', 2, dict(min_length=2)),
    ('', 1, dict(nullable=True)),
    ('-1', 1, dict(rules=[rule.NumericLT(0)])),
    ('-1', 1, dict(rules=[rule.NumericLTE(0)])),
    ('0', 1, dict(rules=[rule.NumericLTE(0)])),
    ('0', 1, dict(rules=[rule.NumericET(0)])),
    ('0', 1, dict(rules=[rule.NumericGTE(0)])),
    ('1', 1, dict(rules=[rule.NumericGTE(0)])),
    ('1', 1, dict(rules=[rule.NumericGT(0)]))
])
def test_integer_good(value, max_length, kwargs):
    assert not Integer(max_length, **kwargs).check(value)


@pytest.mark.parametrize('value,max_length,kwargs,err', [
    ('0', 1, dict(rules=[rule.NumericLT(0)]), ValueComparisonError),
    ('1', 1, dict(rules=[rule.NumericLTE(0)]), ValueComparisonError),
    ('1', 1, dict(rules=[rule.NumericET(0)]), ValueComparisonError),
    ('-1', 1, dict(rules=[rule.NumericGTE(0)]), ValueComparisonError),
    ('0', 1, dict(rules=[rule.NumericGT(0)]), ValueComparisonError),
    ('', 1, {}, NullValueError),
    ('1', 2, dict(min_length=2), LengthError),
    ('111', 2, {}, LengthError),
    ('00', 2, {}, LeadingZeroError),
    ('01', 2, {}, LeadingZeroError)
])
def test_integer_bad(value, max_length, kwargs, err):
    assert Integer(max_length, **kwargs).has_error(value, err)


@pytest.mark.parametrize('value,choices,kwargs', [
    ('x', ['x'], {}),
    ('x', ['x', 'y'], {}),
    ('y', ['x', 'y'], {}),
    ('', ['x'], dict(nullable=True))
])
def test_choice_good(value, choices, kwargs):
    assert not Choice(choices, **kwargs).check(value)


@pytest.mark.parametrize('value,choices,kwargs,err', [
    ('', ['x'], {}, NullValueError),
    ('x', ['z'], {}, InvalidChoiceError)
])
def test_choice_bad(value, choices, kwargs, err):
    assert Choice(choices, **kwargs).has_error(value, err)


def test_row_good(basic):
    assert not Row(Layout(basic)).check(['1', '2', '2020-01-01'])


@pytest.mark.parametrize('value,err', [
    ([1, 2, 3, 4], RowLengthError),
    ([1, 2], RowLengthError)
])
def test_row_bad(basic, value, err):
    assert Row(Layout(basic)).has_error(value, err)


def test_header_good(basic):
    assert not Header(Layout(basic)).check(['col1', 'col2', 'col3'])


@pytest.mark.parametrize('value,err', [
    (['col1', 'col2'], MissingColumnError),
    (['col1', 'col2', 'col2'], DuplicateColumnError),
    (['col1', 'col2', 'col4'], UnexpectedColumnError)
])
def test_header_bad(basic, value, err):
    assert Header(Layout(basic)).has_error(value, err)


def test_file_good(basic_good, basic_definition):
    assert not File(basic_definition).check(basic_good)


def test_layout_good(basic, basic_good):
    assert not Layout(basic).check_file(basic_good)


def test_readme_example(readme_layout, readme_data):
    assert File(Layout(readme_layout)). \
        has_error(readme_data, InvalidChoiceError)


@pytest.mark.parametrize('rows,max_errors', [
    (1, 0),
    (2, 1),
    (101, 100),
    (int(1e5), 100),
])
def test_has_max_error(minimal_layout, tmpdir, rows, max_errors):
    assert File(minimal_layout, max_errors=max_errors). \
        has_error(minimal_bad(rows, tmpdir), MaxExceededError)


@pytest.mark.parametrize('rows,max_errors', [
    (1, 1),
    (99, 100),
    (100, 100),
    (100, int(1e5)),
])
def test_missing_max_error(minimal_layout, tmpdir, rows, max_errors):
    assert not File(minimal_layout, max_errors=max_errors). \
        has_error(minimal_bad(rows, tmpdir), MaxExceededError)


@pytest.mark.parametrize('value,func,assertion', [
    ('2', lambda x: int(x) % 2 == 0, "must be an even number"),
    ('1', lambda x: int(x) % 2 == 1, "must be an odd number"),
    ('2020-01-01', lambda x: dt.fromisoformat(x), "must be an isodate"),
])
def test_static_rules_good(value, func, assertion):
    cell = Cell(rules=[make_static_rule(func, assertion)])
    assert not cell.check(value)


@pytest.mark.parametrize('value,func,assertion,kwargs', [
    ('2', lambda x: int(x) % 2 == 1, "must be an even number", {}),
    ('1', lambda x: int(x) % 2 == 0, "must be an odd number", {}),
    ('2020-00-01', lambda x: dt.fromisoformat(x), "must be an isodate", {}),
    ('', lambda x: 1 / 0, "custom exception", dict(exception=ZeroDivisionError))
])
def test_static_rules_bad(value, func, assertion, kwargs):
    cell = Cell(rules=[make_static_rule(func, assertion, **kwargs)])
    assert cell.has_error(value, kwargs.get('exception', UrNotMyDataError))


def test_column_compare_rule_good():
    cell = Cell(rules=[rule.GreaterThanColumn('x')])
    assert not cell.check('1', compare={'x': '0'})


def test_column_compare_rule_bad():
    cell = Cell(rules=[rule.GreaterThanColumn('x')])
    assert cell.has_error('1', compare={'x': '1'}, error=ColumnComparisonError)


def test_column_compare_row_good():
    row = Row(Layout({
        'a': Integer(1, rules=[rule.GreaterThanColumn('b')]),
        'b': Integer(1)
    }))
    assert not row.check(['3', '2'])


@pytest.mark.parametrize('compare_rule,row', [
    (rule.GreaterThanColumn('x'), ['2', '3']),
])
def test_column_compare_file_good(tmpdir, compare_rule, row):
    lay = Layout({'x': Cell(), 'y': Cell(rules=[compare_rule])})
    assert not lay.check_file(write_row(tmpdir, lay, row))


@pytest.mark.parametrize('compare_rule,row', [
    (rule.GreaterThanColumn('x'), ['1', '1']),
])
def test_column_compare_file_bad(tmpdir, compare_rule, row):
    lay = Layout({'x': Cell(), 'y': Cell(rules=[compare_rule])})
    assert File(lay).has_error(write_row(tmpdir, lay, row), ColumnComparisonError)
