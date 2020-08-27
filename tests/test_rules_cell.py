import pytest

from rumydata.rules.cell import *
from rumydata.rules.cell import Rule


def recurse_subclasses(class_to_recurse):
    def generator(x):
        for y in x.__subclasses__():
            for z in generator(y):
                yield z
        yield x

    return list(generator(class_to_recurse))


@pytest.mark.parametrize('rule', recurse_subclasses(Rule))
def test_rule_prepare(rule):
    """
    All cell preparation must accept a tuple of a value and a dictionary with
    comparison values that may be required.
    """
    r = rule(*rule._default_args)
    assert isinstance(r._prepare(('1', {'x': '0'})), tuple)


@pytest.mark.parametrize('rule', recurse_subclasses(Rule))
def test_rule_evaluator_callable(rule):
    """ All rules must return a callable function """
    assert callable(rule(*rule._default_args)._evaluator())


@pytest.mark.parametrize('value,expected', [
    (' ', True),
    ('1', True),
    ('0', True),
    ('False', True),
    ('', False),
])
def test_not_null(value: str, expected: bool):
    r = NotNull()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('length,value,expected', [
    (1, 'a', True),
    (2, 'a', False),
    (0, 'a', False)
])
def test_exact_char(value: str, expected: bool, length: int):
    r = ExactChar(length)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('length,value,expected', [
    (1, 'a', True),
    (2, 'aa', True),
    (0, 'a', True),
    (2, 'a', False),
    (3, 'aa', False)
])
def test_min_char(value: str, expected: bool, length: int):
    r = MinChar(length)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('length,value,expected', [
    (1, 'a', True),
    (2, 'aa', True),
    (0, 'a', False),
    (2, 'a', True),
    (3, 'aa', True)
])
def test_max_char(value: str, expected: bool, length: int):
    r = MaxChar(length)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
    ('A', True),
    ('aa', True),
    ("\u0394", False)
])
def test_ascii_char(value: str, expected: bool):
    r = AsciiChar()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('choice,value,expected', [
    (['x'], 'x', True),
    (['x'], 'y', False),
    (['x', 'y'], 'y', True)
])
def test_choice(value: str, expected: bool, choice: list):
    r = Choice(choice)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('length,value,expected', [
    (1, 'a', False),
    (2, 'aa', False),
    (2, 'aa1', False),
    (0, 'a', True),  # if no digits are required, 'a' is valid
    (1, '1a', True),
    (2, '111a', True)
])
def test_min_digit(value: str, expected: bool, length: int):
    r = MinDigit(length)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('length,value,expected', [
    (1, 'a', True),
    (2, 'aa', True),
    (2, 'aa1', True),
    (0, 'a', True),  # if no digits are required, 'a' is valid
    (1, '1a', True),
    (2, '111a', False)
])
def test_min_digit(value: str, expected: bool, length: int):
    r = MaxDigit(length)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
    ('123', True),
    ('123a', False),
    ('12.3', False)
])
def test_only_numbers(value: str, expected: bool):
    r = OnlyNumbers()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
    ('0123', False),
    ('1023', True),
    ('0', True),
    ('0.0', False)
])
def test_no_leading_zero(value: str, expected: bool):
    r = NoLeadingZero()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
    ('1', True),
    ('0', True),
    ('a', False),
])
def test_can_be_float(value: str, expected: bool):
    r = CanBeFloat()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
    ('1', True),
    ('0', True),
    ('0.0', False),
    ('0.1', False),
    ('a', False)
])
def test_can_be_integer(value: str, expected: bool):
    r = CanBeInteger()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_numeric_decimals(value: str, expected: bool):
    r = NumericDecimals()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_length_comparison(value: str, expected: bool):
    r = LengthComparison()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_length_gt(value: str, expected: bool):
    r = LengthGT()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_length_gte(value: str, expected: bool):
    r = LengthGTE()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_length_et(value: str, expected: bool):
    r = LengthET()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_length_lte(value: str, expected: bool):
    r = LengthLTE()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_length_lt(value: str, expected: bool):
    r = LengthLT()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_numeric_comparison(value: str, expected: bool):
    r = NumericComparison()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_numeric_gt(value: str, expected: bool):
    r = NumericGT()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_numeric_gte(value: str, expected: bool):
    r = NumericGTE()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_numeric_et(value: str, expected: bool):
    r = NumericET()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_numeric_lte(value: str, expected: bool):
    r = NumericLTE()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_numeric_lt(value: str, expected: bool):
    r = NumericLT()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_date_rule(value: str, expected: bool):
    r = DateRule()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_can_be_date_iso(value: str, expected: bool):
    r = CanBeDateIso()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_date_comparison(value: str, expected: bool):
    r = DateComparison()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_date_gt(value: str, expected: bool):
    r = DateGT()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_date_gte(value: str, expected: bool):
    r = DateGTE()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_date_et(value: str, expected: bool):
    r = DateET()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_date_lte(value: str, expected: bool):
    r = DateLTE()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_date_lt(value: str, expected: bool):
    r = DateLT()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_column_comparison_rule(value: str, expected: bool):
    r = ColumnComparisonRule()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
])
def test_greater_than_column(value: str, expected: bool):
    r = GreaterThanColumn()
    assert r._evaluator()(*r._prepare(value)) is expected
