import pytest

from rumydata.field import Field
from rumydata.rules.header import *
from rumydata.table import Layout


@pytest.mark.parametrize('value,expected,kwargs', [
    (['xyz', 'abc', 'mno'], True, {}),
    (['xyz', 'abc', 'mno', 'x'], False, {}),
    (['xyz123', 'abc456', 'mno789'], False, {}),
    (['xyz123', 'abc456', 'mno789'], True, {'header_mode': 'startswith'}),
    (['1xyz1', '1abc1', '1mno1'], False, {'header_mode': 'startswith'}),
    (['1xyz1', '1abc1', '1mno1'], False, {}),
    (['1xyz1', '1abc1', '1mno1'], True, {'header_mode': 'contains'}),
    (['xyz123', 'abc456', 'mno789'], True, {'header_mode': 'contains'})
])
def test_no_extra(value, expected, kwargs):
    r = NoExtra(Layout({'xyz': Field(), 'abc': Field(), 'mno': Field()}, **kwargs))
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected,kwargs', [
    (['xyz', 'abc', 'mno'], True, {}),
    (['xyz', 'abc', 'mno', 'efg'], True, {}),
    (['xyz', 'abc', 'mno'], True, {}),
    (['abc', 'mno', 'efg'], False, {}),
    (['xyz', 'abc'], False, {}),
    (['xyz123', 'abc456', 'mno789'], True, {'header_mode': 'startswith'}),
    (['xyz123', 'abc456', '789mno'], False, {'header_mode': 'startswith'}),
    (['1xyz1', '1abc1', '1mno1'], False, {'header_mode': 'startswith'}),
    (['1xyz1', '1abc1', '1mno1'], True, {'header_mode': 'contains'}),
    (['xyz123', 'abc456', 'mno789'], True, {'header_mode': 'contains'}),
    (['123', 'abc456', 'mno789'], False, {'header_mode': 'contains'})
])
def test_no_missing(value, expected, kwargs):
    r = NoMissing(Layout({'xyz': Field(), 'abc': Field(), 'mno': Field()}, **kwargs))
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected,kwargs', [
    (['xyz', 'abc', 'mno'], True, {}),
    (['xyz', 'abc', 'abc'], False, {}),
    (['xyz123', 'abc456', 'mno789'], True, {'header_mode': 'startswith'}),
    (['xyz123', 'xyz456'], False, {'header_mode': 'startswith'}),
    (['1xyz2', '1abc2', '1mno2'], True, {'header_mode': 'contains'}),
    (['1xyz2', '111xyz222'], False, {'header_mode': 'contains'}),
])
def test_no_duplicate(value, expected, kwargs):
    r = NoDuplicate(Layout({'xyz': Field(), 'abc': Field(), 'mno': Field()}, **kwargs))
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected,kwargs', [
    (['xyz', 'abc', 'mno'], True, {}),
    (['xyz', 'mno', 'abc'], False, {}),
    (['xyz1', 'abc2', 'mno3'], True, {'header_mode': 'startswith'}),
    (['xyz1', 'mno3', 'abc2'], False, {'header_mode': 'startswith'}),
    (['1xyz1', '1abc2', '1mno3'], True, {'header_mode': 'contains'}),
    (['1xyz1', '1mno3', '1abc2'], False, {'header_mode': 'contains'}),
])
def test_column_order(value, expected, kwargs):
    r = ColumnOrder(Layout({'xyz': Field(), 'abc': Field(), 'mno': Field()}, **kwargs))
    assert r._evaluator()(*r._prepare(value)) is expected


def test_invalid_header_mode():
    with pytest.raises(ValueError):
        Layout({}, header_mode='x')
