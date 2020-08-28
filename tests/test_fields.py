from datetime import datetime as dt

import pytest

from rumydata import exception as ex, field, rules


def recurse_subclasses(class_to_recurse):
    def generator(x):
        for y in x.__subclasses__():
            for z in generator(y):
                yield z
        yield x

    return list(generator(class_to_recurse))


@pytest.mark.parametrize('fo,rule', [
    (field.Text(1), rules.cell.MaxChar),
    (field.Text(1, 2), rules.cell.MinChar),
    (field.Text(1, rules=[rules.cell.AsciiChar()]), rules.cell.AsciiChar)
])
def test_has_rule(fo, rule):
    assert fo._has_rule_type(rule)


@pytest.mark.parametrize('fo,columns', [
    (field.Field(rules=[rules.cell.GreaterThanColumn('x')]), set('x')),
    (field.Field(
        rules=[rules.cell.GreaterThanColumn('x'), rules.cell.GreaterThanColumn('y')]
    ), {'x', 'y'}),
    (field.Field(rules=[]), set())
])
def test_comparison_columns(fo, columns: set):
    assert fo._comparison_columns() == columns


@pytest.mark.parametrize('fo', recurse_subclasses(field.Field))
def test_digest(fo):
    assert isinstance(fo(*fo._default_args)._digest(), list)


@pytest.mark.parametrize('value,kwargs', [
    ('x', dict(max_length=1)),
    ('x', dict(max_length=2)),
    ('', dict(max_length=1, nullable=True)),
    ('', dict(max_length=1, min_length=1, nullable=True))
])
def test_text_good(value, kwargs):
    assert not field.Text(**kwargs).check_cell(value)


@pytest.mark.parametrize('value,kwargs,err', [
    ('', dict(max_length=1), ex.NullValueError),
    ('xxx', dict(max_length=2), ex.LengthError),
    ('x', dict(max_length=80, min_length=2), ex.LengthError),
])
def test_text_bad(value, kwargs, err):
    assert field.Text(**kwargs)._has_error(value, err)


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
    assert field.Date(**kwargs)._has_error(value, err)


@pytest.mark.parametrize('value,sig_dig,kwargs', [
    ('123.45', 5, {}),
    ('123.00', 5, {}),
    ('123.0', 5, {}),
    ('123', 5, {}),
    ('', 1, dict(nullable=True)),
    ('-0.01', 3, dict(rules=[rules.cell.NumericLT(0)])),
    ('0', 3, dict(rules=[rules.cell.NumericLTE(0)])),
    ('0.00', 3, dict(rules=[rules.cell.NumericET(0)])),
    ('0', 3, dict(rules=[rules.cell.NumericGTE(0)])),
    ('0.01', 3, dict(rules=[rules.cell.NumericGT(0)])),
])
def test_currency_good(value, sig_dig, kwargs):
    assert not field.Currency(sig_dig, **kwargs).check_cell(value)


@pytest.mark.parametrize('value,sig_dig,rules,err', [
    ('0.00', 5, [rules.cell.NumericLT(0)], ex.ValueComparisonError),
    ('0.01', 5, [rules.cell.NumericLTE(0)], ex.ValueComparisonError),
    ('0.01', 5, [rules.cell.NumericET(0)], ex.ValueComparisonError),
    ('-0.01', 5, [rules.cell.NumericGTE(0)], ex.ValueComparisonError),
    ('-0.01', 5, [rules.cell.NumericGT(0)], ex.ValueComparisonError),
    ('', 5, [], ex.NullValueError),
    ('123.45', 4, [], ex.LengthError),
    ('123.', 4, [], ex.CurrencyPatternError),
    ('123.456', 4, [], ex.CurrencyPatternError)
])
def test_currency_bad(value, sig_dig, rules, err):
    assert field.Currency(sig_dig, rules=rules)._has_error(value, err)


@pytest.mark.parametrize('value,max_length, kwargs', [
    ('1', 3, {}),
    ('12', 3, {}),
    ('123', 3, {}),
    ('12', 2, dict(min_length=2)),
    ('123', 3, dict(min_length=2))
])
def test_digit_good(value, max_length, kwargs):
    assert not field.Digit(max_length, **kwargs).check_cell(value)


@pytest.mark.parametrize('value,max_length,err,kwargs', [
    ('-123', 3, ex.CharacterError, {}),
    ('-123', 3, ex.LengthError, {}),
    ('1', 2, ex.LengthError, dict(min_length=2)),
    ('5', 3, ex.LengthError, dict(min_length=2))
])
def test_digit_bad(value, max_length, err, kwargs):
    assert field.Digit(max_length, **kwargs)._has_error(value, err)


@pytest.mark.parametrize('value,max_length,kwargs', [
    ('-1', 1, {}),
    ('0', 1, {}),
    ('1', 1, {}),
    ('1', 2, {}),
    ('11', 2, dict(min_length=2)),
    ('', 1, dict(nullable=True)),
    ('-1', 1, dict(rules=[rules.cell.NumericLT(0)])),
    ('-1', 1, dict(rules=[rules.cell.NumericLTE(0)])),
    ('0', 1, dict(rules=[rules.cell.NumericLTE(0)])),
    ('0', 1, dict(rules=[rules.cell.NumericET(0)])),
    ('0', 1, dict(rules=[rules.cell.NumericGTE(0)])),
    ('1', 1, dict(rules=[rules.cell.NumericGTE(0)])),
    ('1', 1, dict(rules=[rules.cell.NumericGT(0)]))
])
def test_integer_good(value, max_length, kwargs):
    assert not field.Integer(max_length, **kwargs).check_cell(value)


@pytest.mark.parametrize('value,max_length,kwargs,err', [
    ('0', 1, dict(rules=[rules.cell.NumericLT(0)]), ex.ValueComparisonError),
    ('1', 1, dict(rules=[rules.cell.NumericLTE(0)]), ex.ValueComparisonError),
    ('1', 1, dict(rules=[rules.cell.NumericET(0)]), ex.ValueComparisonError),
    ('-1', 1, dict(rules=[rules.cell.NumericGTE(0)]), ex.ValueComparisonError),
    ('0', 1, dict(rules=[rules.cell.NumericGT(0)]), ex.ValueComparisonError),
    ('', 1, {}, ex.NullValueError),
    ('1', 2, dict(min_length=2), ex.LengthError),
    ('111', 2, {}, ex.LengthError),
    ('00', 2, {}, ex.LeadingZeroError),
    ('01', 2, {}, ex.LeadingZeroError)
])
def test_integer_bad(value, max_length, kwargs, err):
    assert field.Integer(max_length, **kwargs)._has_error(value, err)


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
    assert field.Choice(choices, **kwargs)._has_error(value, err)


@pytest.mark.parametrize('value,func,assertion', [
    ('2', lambda x: int(x) % 2 == 0, "must be an even number"),
    ('1', lambda x: int(x) % 2 == 1, "must be an odd number"),
    ('2020-01-01', lambda x: dt.fromisoformat(x), "must be an isodate"),
])
def test_static_rules_good(value, func, assertion):
    x = field.Field(rules=[rules.cell.make_static_cell_rule(func, assertion)])
    assert not x.check_cell(value)


@pytest.mark.parametrize('value,func,assertion,kwargs', [
    ('2', lambda x: int(x) % 2 == 1, "must be an even number", {}),
    ('1', lambda x: int(x) % 2 == 0, "must be an odd number", {}),
    ('2020-00-01', lambda x: dt.fromisoformat(x), "must be an isodate", {}),
    ('', lambda x: 1 / 0, "custom exception", dict(exception=ZeroDivisionError))
])
def test_static_rules_bad(value, func, assertion, kwargs):
    x = field.Field(rules=[rules.cell.make_static_cell_rule(func, assertion, **kwargs)])
    assert x._has_error(value, kwargs.get('exception', ex.UrNotMyDataError))


@pytest.mark.parametrize('cell', [
    '',
    '1',
    '8k;abc;abc'
])
def test_ignore_cell(cell):
    assert not field.Ignore().check_cell(cell)


def test_column_compare_rule_good():
    x = field.Field(rules=[rules.cell.GreaterThanColumn('x')])
    assert not x.check_cell(('1', {'x': '0'}))


def test_column_compare_rule_bad():
    x = field.Field(rules=[rules.cell.GreaterThanColumn('x')])
    assert x._has_error('1', compare={'x': '1'}, error=ex.ColumnComparisonError)


def test_column_unique_good():
    x = field.Field(rules=[rules.column.Unique()])
    assert not x.check_column(['1', '2', '3'])


def test_column_unique_bad():
    x = field.Field(rules=[rules.column.Unique()])
    assert x._has_error(['2', '2'], ex.DuplicateValueError, rule_type=field.cr.Rule)
