from datetime import datetime as dt

import pytest

from rumydata import field, rules, exception as ex




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


def test_empty_field():
    empty = field.Empty()
    assert not empty.check_cell('')
    with pytest.raises(AssertionError):
        assert empty.check_cell('1')


def test_custom_message():
    f = field.Text(1, custom_error_msg='CustomErrorMessage')
    t = f._has_error('', ex.CustomError)
    assert t


def test_no_errors():
    f = field.Text(1, all_errors=False)
    e = f._list_errors('')
    he = f._has_error('', ex.CellError)
    assert len(e) == 1 and he


def test_custom_message_override():
    f = field.Text(1, custom_error_msg='CustomErrorMessage', all_errors=False)
    e = f._list_errors('')
    cuse = f._has_error('', ex.CustomError)
    cele = f._has_error('', ex.CellError)
    assert all([len(e) == 2, cuse, cele])
