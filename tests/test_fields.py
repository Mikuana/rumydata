from datetime import datetime as dt

import pytest

from rumydata import field, rules


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


@pytest.mark.parametrize('value,kwargs,rule', [
    ('', dict(max_length=1), rules.cell.NotNull),
    ('xxx', dict(max_length=2), rules.cell.MaxChar),
    ('x', dict(max_length=80, min_length=2), rules.cell.MinChar),
])
def test_text_bad(value, kwargs, rule):
    assert field.Text(**kwargs)._has_error(value, rule.rule_exception())


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


@pytest.mark.parametrize('value,rule,kwargs', [
    ('', rules.cell.NotNull, {}),
    ('20200101', rules.cell.CanBeDateIso, {}),
    ('9999-99-99', rules.cell.CanBeDateIso, {}),
    ('2020-01-01', rules.cell.DateGTE, dict(min_date='2020-01-02')),
    ('2020-01-02', rules.cell.DateLTE, dict(max_date='2020-01-01')),
    ('2020-01-01', rules.cell.DateGTE, dict(min_date='2020-01-02', max_date='2020-01-03')),
    ('2020-01-05', rules.cell.DateLTE, dict(min_date='2020-01-02', max_date='2020-01-03')),
    ('2020-01-01 00:00:00', rules.cell.CanBeDateIso, dict(truncate_time=True)),
    ('2020-01-01 00:00:01', rules.cell.CanBeDateIso, dict(truncate_time=False))
])
def test_date_bad(value, rule, kwargs):
    assert field.Date(**kwargs)._has_error(value, rule.rule_exception())


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


@pytest.mark.parametrize('value,sig_dig,rules_list,err', [
    ('0.00', 5, [rules.cell.NumericLT(0)], rules.cell.NumericLT),
    ('0.01', 5, [rules.cell.NumericLTE(0)], rules.cell.NumericLTE),
    ('0.01', 5, [rules.cell.NumericET(0)], rules.cell.NumericET),
    ('-0.01', 5, [rules.cell.NumericGTE(0)], rules.cell.NumericGTE),
    ('-0.01', 5, [rules.cell.NumericGT(0)], rules.cell.NumericGT),
    ('', 5, [], rules.cell.NotNull),
    ('123.45', 4, [], rules.cell.MaxDigit),
    ('123.', 4, [], rules.cell.NumericDecimals),
    ('123.456', 4, [], rules.cell.NumericDecimals)
])
def test_currency_bad(value, sig_dig, rules_list, err):
    assert field.Currency(sig_dig, rules=rules_list)._has_error(value, err.rule_exception())


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
    ('-123', 3, rules.cell.OnlyNumbers, {}),
    ('-123', 3, rules.cell.MaxChar, {}),
    ('1', 2, rules.cell.MinChar, dict(min_length=2)),
    ('123456', 3, rules.cell.MaxChar, dict(min_length=2))
])
def test_digit_bad(value, max_length, err, kwargs):
    assert field.Digit(max_length, **kwargs)._has_error(value, err.rule_exception())


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
    ('0', 1, dict(rules=[rules.cell.NumericLT(0)]), rules.cell.NumericLT),
    ('1', 1, dict(rules=[rules.cell.NumericLTE(0)]), rules.cell.NumericLTE),
    ('1', 1, dict(rules=[rules.cell.NumericET(0)]), rules.cell.NumericET),
    ('-1', 1, dict(rules=[rules.cell.NumericGTE(0)]), rules.cell.NumericGTE),
    ('0', 1, dict(rules=[rules.cell.NumericGT(0)]), rules.cell.NumericGT),
    ('', 1, {}, rules.cell.NotNull),
    ('1', 2, dict(min_length=2), rules.cell.MinDigit),
    ('111', 2, {}, rules.cell.MaxDigit),
    ('00', 2, {}, rules.cell.NoLeadingZero),
    ('01', 2, {}, rules.cell.NoLeadingZero)
])
def test_integer_bad(value, max_length, kwargs, err):
    assert field.Integer(max_length, **kwargs)._has_error(value, err.rule_exception())


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
    ('', ['x'], {}, rules.cell.NotNull),
    ('x', ['z'], {}, rules.cell.Choice)
])
def test_choice_bad(value, choices, kwargs, err):
    assert field.Choice(choices, **kwargs)._has_error(value, err.rule_exception())


@pytest.mark.parametrize('value,func,assertion', [
    ('2', lambda x: int(x) % 2 == 0, "must be an even number"),
    ('1', lambda x: int(x) % 2 == 1, "must be an odd number"),
    ('2020-01-01', lambda x: dt.fromisoformat(x), "must be an isodate"),
])
def test_static_rules_good(value, func, assertion):
    x = field.Field(rules=[rules.cell.make_static_cell_rule(func, assertion)])
    assert not x.check_cell(value)


@pytest.mark.parametrize('value,func,assertion', [
    ('2', lambda x: int(x) % 2 == 1, "must be an even number"),
    ('1', lambda x: int(x) % 2 == 0, "must be an odd number"),
    ('2020-00-01', lambda x: dt.fromisoformat(x), "must be an isodate"),
    ('', lambda x: 1 / 0, "custom exception")
])
def test_static_rules_bad(value, func, assertion):
    r = rules.cell.make_static_cell_rule(func, assertion)
    x = field.Field(rules=[r])
    assert x._has_error(value, r.rule_exception())


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
    assert x._has_error('1', compare={'x': '1'}, error=rules.cell.GreaterThanColumn.rule_exception())


def test_column_unique_good():
    x = field.Field(rules=[rules.column.Unique()])
    assert not x.check_column(['1', '2', '3'])


def test_column_unique_bad():
    x = field.Field(rules=[rules.column.Unique()])
    assert x._has_error(['2', '2'], rules.column.Unique.rule_exception(), rule_type=field.cr.Rule)
