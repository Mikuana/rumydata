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


@pytest.mark.parametrize('choice,data,expected,kwargs', [
    (['x'], 'x', True, {}),
    (['x'], 'y', False, {}),
    (['x', 'y'], 'y', True, {}),
    (['x'], ('x', {}), True, {}),
    (['X'], ('x', {}), True, dict(case_insensitive=True))
])
def test_choice(data, expected: bool, choice: list, kwargs):
    r = Choice(choice, **kwargs)
    assert r._evaluator()(*r._prepare(data)) is expected


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
def test_max_digit(value: str, expected: bool, length: int):
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


@pytest.mark.parametrize('decimals,value,expected', [
    (1, '1.0', True),
    (1, '123', True),
    (1, '0123', True),  # combine with NoLeadingZero to prevent this
    (1, '1.00', False),
    (2, '1.00', True)
])
def test_numeric_decimals(decimals: int, value: str, expected: bool):
    r = NumericDecimals(decimals)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    (1, 'x', False),
    (1, 'xx', True),
    (2, 'xx', False)
])
def test_length_gt(comparison: int, value: str, expected: bool):
    r = LengthGT(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    (1, 'x', True),
    (1, 'xx', True),
    (3, 'xx', False)
])
def test_length_gte(comparison: int, value: str, expected: bool):
    r = LengthGTE(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    (1, 'x', True),
    (2, 'xx', True),
    (3, 'xx', False)
])
def test_length_et(comparison: int, value: str, expected: bool):
    r = LengthET(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    (1, 'x', True),
    (2, 'xx', True),
    (3, 'xx', True),
    (0, 'x', False)
])
def test_length_lte(comparison: int, value: str, expected: bool):
    r = LengthLTE(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    (1, 'x', False),
    (2, 'xx', False),
    (3, 'xx', True),
    (0, 'x', False)
])
def test_length_lt(comparison: int, value: str, expected: bool):
    r = LengthLT(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    (1, '1', False),
    (1, '2', True),
    (1, '1.1', True),
    (0, '0', False)
])
def test_numeric_gt(comparison: float, value: str, expected: bool):
    r = NumericGT(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    (1, '1', True),
    (1, '2', True),
    (1, '1.1', True),
    (1, '1.0', True),
    (0, '0', True),
    (1, '0', False)
])
def test_numeric_gte(comparison: float, value: str, expected: bool):
    r = NumericGTE(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    (1, '1', True),
    (1, '2', False),
    (1, '1.1', False),
    (1, '1.0', True),
    (0, '0', True),
    (1, '0', False)
])
def test_numeric_et(comparison: float, value: str, expected: bool):
    r = NumericET(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    (1, '1', True),
    (1, '2', False),
    (1, '1.1', False),
    (1, '1.0', True),
    (0, '0', True),
    (1, '0', True)
])
def test_numeric_lte(comparison: float, value: str, expected: bool):
    r = NumericLTE(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    (1, '1', False),
    (1, '2', False),
    (1, '1.1', False),
    (1, '1.0', False),
    (1, '0.9', True),
    (0, '0', False),
    (1, '0', True)
])
def test_numeric_lt(comparison: float, value: str, expected: bool):
    r = NumericLT(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected,kwargs', [
    ('2020-01-01', True, {}),
    ('2020/01/01', False, {}),
    ('1901-01-01', True, {}),
    ('19010101', False, {}),
    ('9999-99-99', False, {}),
    ('2020-13-01', False, {}),
    ('2020-01-01', True, dict(truncate_time=True)),
    ('2020-01-01 00:00:00', True, dict(truncate_time=True)),
    (('2020-01-01 00:00:00', {}), True, dict(truncate_time=True)),
    ('2020-01-01 00:00:01', False, dict(truncate_time=True))
])
def test_can_be_date_iso(value: str, expected: bool, kwargs: dict):
    r = CanBeDateIso(**kwargs)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    ('2020-01-01', '2020-01-01', False),
    ('2020-01-01', '2020-01-02', True),
    ('2020-01-01', '2020-01-32', False),
    ('2020-01-01', '2019-12-31', False)
])
def test_date_gt(comparison: str, value: str, expected: bool):
    r = DateGT(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    ('2020-01-01', '2020-01-01', True),
    ('2020-01-01', '2020-01-02', True),
    ('2020-01-01', '2020-01-32', False),
    ('2020-01-01', '2019-12-31', False)
])
def test_date_gte(comparison: str, value: str, expected: bool):
    r = DateGTE(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    ('2020-01-01', '2020-01-01', True),
    ('2020-01-01', '2020-01-02', False),
    ('2020-01-01', '2020-01-32', False),
    ('2020-01-01', '2019-12-31', False)
])
def test_date_et(comparison: str, value: str, expected: bool):
    r = DateET(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    ('2020-01-01', '2020-01-01', True),
    ('2020-01-01', '2020-01-02', False),
    ('2020-01-01', '2020-01-32', False),
    ('2020-01-01', '2019-12-31', True)
])
def test_date_lte(comparison: str, value: str, expected: bool):
    r = DateLTE(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    ('2020-01-01', '2020-01-01', False),
    ('2020-01-01', '2020-01-02', False),
    ('2020-01-01', '2020-01-32', False),
    ('2020-01-01', '2019-12-31', True)
])
def test_date_lt(comparison: str, value: str, expected: bool):
    r = DateLT(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('compared,data,expected', [
    ('x', ('1', {'x': '0'}), True),
    ('x', ('1', {'x': '1'}), False),
    ('z', ('1', {'x': '1', 'z': '0'}), True)
])
def test_greater_than_column(compared: str, data, expected: bool):
    r = GreaterThanColumn(compared)
    assert r._evaluator()(*r._prepare(data)) is expected
