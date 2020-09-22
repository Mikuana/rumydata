import pytest

from rumydata.field import Field
from rumydata.rules.header import *
from rumydata.table import Layout


@pytest.mark.parametrize('value,expected,kwargs', [
    (['xyz', 'abc', 'mno'], True, {}),
    (['xyz', 'abc', 'mno', 'x'], False, {}),
    (['x', 'a', 'm'], False, {}),
    (['x', 'a', 'm'], True, {'header_mode': 'startswith'}),
    (['y', 'b', 'n'], False, {}),
    (['y', 'b', 'n'], True, {'header_mode': 'contains'})
])
def test_no_extra(value, expected, kwargs):
    r = NoExtra(Layout({'xyz': Field(), 'abc': Field(), 'mno': Field()}, **kwargs))
    assert r._evaluator()(*r._prepare(value)) is expected


def test_no_missing():
    assert False


def test_no_duplicate():
    assert False


def test_column_order():
    assert False
