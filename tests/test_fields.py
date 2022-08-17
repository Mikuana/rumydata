from datetime import datetime as dt

import pytest

from rumydata import field, rules, exception as ex
from tests.utils import file_cell_harness, file_row_harness


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
    fld = field.Text(**kwargs)
    assert not fld.check_cell(value)
    assert not file_cell_harness(value, fld)


@pytest.mark.parametrize('value,kwargs,rule', [
    ('', dict(max_length=1), rules.cell.NotNull),
    ('xxx', dict(max_length=2), rules.cell.MaxChar),
    ('x', dict(max_length=80, min_length=2), rules.cell.MinChar),
])
def test_text_bad(value, kwargs, rule):
    fld = field.Text(**kwargs)
    assert fld._has_error(value, rule.rule_exception())
    with pytest.raises(AssertionError):
        file_cell_harness(value, fld)


@pytest.mark.parametrize('value,kwargs', [
    ('2020-01-01', {}),
    ('', dict(nullable=True)),
    ('2020-01-01', dict(max_date='2020-01-01')),
    ('2020-01-01', dict(max_date='2020-01-02')),
    ('2020-01-01', dict(min_date='2020-01-01', max_date='2020-01-02')),
    ('2020-01-01 00:00:00', dict(truncate_time=True))
])
def test_date_good(value, kwargs):
    fld = field.Date(**kwargs)
    assert not fld.check_cell(value)
    assert not file_cell_harness(value, fld)


@pytest.mark.parametrize('value,rule,kwargs', [
    ('', rules.cell.NotNull, {}),
    ('20200101', rules.cell.CanBeDateIso, {}),
    ('9999-99-99', rules.cell.CanBeDateIso, {}),
    ('2020-01-01', rules.cell.DateGTE, dict(min_date='2020-01-02')),
    ('2020-01-02', rules.cell.DateLTE, dict(max_date='2020-01-01')),
    ('2020-01-01', rules.cell.DateGTE, dict(min_date='2020-01-02', max_date='2020-01-03')),
    ('2020-01-05', rules.cell.DateLTE, dict(min_date='2020-01-02', max_date='2020-01-03')),
    ('2020-01-01 00:00:01', rules.cell.CanBeDateIso, dict(truncate_time=False))
])
def test_date_bad(value, rule, kwargs):
    fld = field.Date(**kwargs)
    assert fld._has_error(value, rule.rule_exception(), rule_type=rules.cell.Rule)
    with pytest.raises(AssertionError):
        file_cell_harness(value, fld)


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
    ('0.1', 4, dict(precision=4)),
    ('0.001', 4, dict(precision=3)),
    ('0.0001', 5, dict(precision=4)),
])
def test_currency_good(value, sig_dig, kwargs):
    fld = field.Currency(sig_dig, **kwargs)
    assert not fld.check_cell(value)
    file_cell_harness(value, fld)


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
    fld = field.Currency(sig_dig, rules=rules_list)
    assert fld._has_error(value, err.rule_exception())
    with pytest.raises(AssertionError):
        file_cell_harness(value, fld)


@pytest.mark.parametrize('value,max_length, kwargs', [
    ('1', 3, {}),
    ('12', 3, {}),
    ('123', 3, {}),
    ('12', 2, dict(min_length=2)),
    ('123', 3, dict(min_length=2))
])
def test_digit_good(value, max_length, kwargs):
    fld = field.Digit(max_length, **kwargs)
    assert not fld.check_cell(value)
    file_cell_harness(value, fld)


@pytest.mark.parametrize('value,max_length,err,kwargs', [
    ('-123', 3, rules.cell.OnlyNumbers, {}),
    ('-123', 3, rules.cell.MaxChar, {}),
    ('1', 2, rules.cell.MinChar, dict(min_length=2)),
    ('123456', 3, rules.cell.MaxChar, dict(min_length=2))
])
def test_digit_bad(value, max_length, err, kwargs):
    fld = field.Digit(max_length, **kwargs)
    assert fld._has_error(value, err.rule_exception())
    with pytest.raises(AssertionError):
        file_cell_harness(value, fld)


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
    fld = field.Integer(max_length, **kwargs)
    assert not fld.check_cell(value)
    file_cell_harness(value, fld)


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
    fld = field.Integer(max_length, **kwargs)
    assert fld._has_error(value, err.rule_exception())
    with pytest.raises(AssertionError):
        file_cell_harness(value, fld)


@pytest.mark.parametrize('value,choices,kwargs', [
    ('x', ['x'], {}),
    ('x', ['x', 'y'], {}),
    ('y', ['x', 'y'], {}),
    ('', ['x'], dict(nullable=True)),
    ('X', ['x'], dict(case_insensitive=True)),
    ('x', ['X'], dict(case_insensitive=True))
])
def test_choice_good(value, choices, kwargs):
    fld = field.Choice(choices, **kwargs)
    assert not fld.check_cell(value)
    file_cell_harness(value, fld)


@pytest.mark.parametrize('value,choices,kwargs,err', [
    ('', ['x'], {}, rules.cell.NotNull),
    ('x', ['z'], {}, rules.cell.Choice)
])
def test_choice_bad(value, choices, kwargs, err):
    fld = field.Choice(choices, **kwargs)
    assert fld._has_error(value, err.rule_exception())
    with pytest.raises(AssertionError):
        file_cell_harness(value, fld)


@pytest.mark.parametrize('value,func,assertion', [
    ('2', lambda x: int(x) % 2 == 0, "must be an even number"),
    ('1', lambda x: int(x) % 2 == 1, "must be an odd number"),
    ('2020-01-01', lambda x: dt.fromisoformat(x), "must be an isodate"),
])
def test_static_rules_good(value, func, assertion):
    x = field.Field(rules=[rules.cell.make_static_cell_rule(func, assertion)])
    assert not x.check_cell(value)
    file_cell_harness(value, x)


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
    with pytest.raises(AssertionError):
        file_cell_harness(value, x)


@pytest.mark.parametrize('cell', [
    '',
    '1',
    '8k;abc;abc'
])
def test_ignore_cell(cell):
    fld = field.Ignore()
    assert not fld.check_cell(cell)
    file_cell_harness(cell, fld)


def test_column_compare_rule_good():
    value = ('1', {'x': '0'})
    x = field.Field(rules=[rules.cell.GreaterThanColumn('x')])
    assert not x.check_cell(value)


def test_column_compare_rule_good_files():
    value = ['1', '0']
    lay = {'c1': field.Field(rules=[rules.cell.GreaterThanColumn('c2')]), 'c2': field.Integer(1)}
    file_row_harness(value, lay)


def test_column_compare_rule_bad():
    x = field.Field(rules=[rules.cell.GreaterThanColumn('x')])
    assert x._has_error('1', compare={'x': '1'}, error=rules.cell.GreaterThanColumn.rule_exception())
    with pytest.raises(AssertionError):
        file_row_harness(['1', '0'], dict(x=field.Integer(1), y=x))


def test_column_unique_good():
    x = field.Field(rules=[rules.column.Unique()])
    assert not x.check_column(['1', '2', '3'])
    file_row_harness(['1', '2', '3'], dict(x=x, y=field.Ignore(), z=field.Ignore()))


def test_column_unique_bad():
    x = field.Field(rules=[rules.column.Unique()])
    assert x._has_error(['2', '2'], rules.column.Unique.rule_exception(), rule_type=field.cr.Rule)
    file_row_harness(['2', '2'], dict(x=x, y=x))


def test_empty_field():
    empty = field.Empty()
    assert not empty.check_cell('')
    file_cell_harness('', empty)
    with pytest.raises(AssertionError):
        assert empty.check_cell('1')
    with pytest.raises(AssertionError):
        file_cell_harness('1', empty)


def test_custom_message():
    assert not field.Text(1, custom_error_msg='CustomErrorMessage')._has_error('1', ex.CustomError,
                                                                               rule_type=rules.cell.Rule)
    assert field.Text(1, custom_error_msg='CustomErrorMessage')._has_error('', ex.CustomError,
                                                                           rule_type=rules.cell.Rule)


def test_no_errors():
    assert not len(field.Text(1, all_errors=False)._list_errors('', rule_type=rules.cell.Rule)) > 1
    assert len(field.Text(1, all_errors=True)._list_errors('', rule_type=rules.cell.Rule)) > 1


def test_custom_message_override():
    assert not len(field.Text(1, custom_error_msg='CustomErrorMessage', all_errors=False)._list_errors('',
                                                                                                       rule_type=rules.cell.Rule)) > 2
    assert len(field.Text(1, custom_error_msg='CustomErrorMessage', all_errors=True)._list_errors('',
                                                                                                  rule_type=rules.cell.Rule)) > 2
