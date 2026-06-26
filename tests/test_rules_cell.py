import pytest

from rumydata.rules import cell
from rumydata.rules.cell import Rule


def recurse_subclasses(class_to_recurse):
    def generator(x):
        for y in x.__subclasses__():
            yield from generator(y)
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
    r = cell.NotNull()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('length,value,expected', [
    (1, 'a', True),
    (2, 'a', False),
    (0, 'a', False)
])
def test_exact_char(value: str, expected: bool, length: int):
    r = cell.ExactChar(length)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('length,value,expected', [
    (1, 'a', True),
    (2, 'aa', True),
    (0, 'a', True),
    (2, 'a', False),
    (3, 'aa', False)
])
def test_min_char(value: str, expected: bool, length: int):
    r = cell.MinChar(length)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('length,value,expected', [
    (1, 'a', True),
    (2, 'aa', True),
    (0, 'a', False),
    (2, 'a', True),
    (3, 'aa', True)
])
def test_max_char(value: str, expected: bool, length: int):
    r = cell.MaxChar(length)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
    ('A', True),
    ('aa', True),
    ("\u0394", False)
])
def test_ascii_char(value: str, expected: bool):
    r = cell.AsciiChar()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('choice,data,expected,kwargs', [
    (['x'], 'x', True, {}),
    (['x'], 'y', False, {}),
    (['x', 'y'], 'y', True, {}),
    (['x'], ('x', {}), True, {}),
    (['X'], ('x', {}), True, {'case_insensitive': True})
])
def test_choice(data, expected: bool, choice: list, kwargs):
    r = cell.Choice(choice, **kwargs)
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
    r = cell.MinDigit(length)
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
    r = cell.MaxDigit(length)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
    ('123', True),
    ('123a', False),
    ('12.3', False)
])
def test_only_numbers(value: str, expected: bool):
    r = cell.OnlyNumbers()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
    ('0123', False),
    ('1023', True),
    ('0', True),
    ('0.0', False)
])
def test_no_leading_zero(value: str, expected: bool):
    r = cell.NoLeadingZero()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
    ('1', True),
    ('0', True),
    ('0.1', True),
    ('a', False),
    ('+3', True),
    ('3.2e23', True),
    ('-4.70e+9', True),
    ('-.2E-4', True),
    ('-7.6603', True),
    ('+0003 ', True),
    ('37.e88', True)
])
def test_can_be_float(value: str, expected: bool):
    r = cell.CanBeFloat()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected', [
    ('1', True),
    ('0', True),
    ('0.0', False),
    ('0.1', False),
    ('a', False)
])
def test_can_be_integer(value: str, expected: bool):
    r = cell.CanBeInteger()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('decimals,value,expected', [
    (1, '1.0', True),
    (1, '123', True),
    (1, '0123', True),  # combine with NoLeadingZero to prevent this
    (1, '1.00', False),
    (2, '1.00', True)
])
def test_numeric_decimals(decimals: int, value: str, expected: bool):
    r = cell.NumericDecimals(decimals)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    (1, 'x', False),
    (1, 'xx', True),
    (2, 'xx', False)
])
def test_length_gt(comparison: int, value: str, expected: bool):
    r = cell.LengthGT(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    (1, 'x', True),
    (1, 'xx', True),
    (3, 'xx', False)
])
def test_length_gte(comparison: int, value: str, expected: bool):
    r = cell.LengthGTE(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    (1, 'x', True),
    (2, 'xx', True),
    (3, 'xx', False)
])
def test_length_et(comparison: int, value: str, expected: bool):
    r = cell.LengthET(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    (1, 'x', True),
    (2, 'xx', True),
    (3, 'xx', True),
    (0, 'x', False)
])
def test_length_lte(comparison: int, value: str, expected: bool):
    r = cell.LengthLTE(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    (1, 'x', False),
    (2, 'xx', False),
    (3, 'xx', True),
    (0, 'x', False)
])
def test_length_lt(comparison: int, value: str, expected: bool):
    r = cell.LengthLT(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    (1, '1', False),
    (1, '2', True),
    (1, '1.1', True),
    (0, '0', False)
])
def test_numeric_gt(comparison: float, value: str, expected: bool):
    r = cell.NumericGT(comparison)
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
    r = cell.NumericGTE(comparison)
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
    r = cell.NumericET(comparison)
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
    r = cell.NumericLTE(comparison)
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
    r = cell.NumericLT(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value,expected,kwargs', [
    ('2020-01-01', True, {}),
    ('2020/01/01', False, {}),
    ('1901-01-01', True, {}),
    ('19010101', False, {}),
    ('9999-99-99', False, {}),
    ('2020-13-01', False, {}),
    ('2020-01-01', True, {'truncate_time': True}),
    ('2020-01-01 00:00:00', True, {'truncate_time': True}),
    (('2020-01-01 00:00:00', {}), True, {'truncate_time': True}),
    ('2020-01-01 00:00:01', False, {'truncate_time': True})
])
def test_can_be_date_iso(value: str, expected: bool, kwargs: dict):
    r = cell.CanBeDateIso(**kwargs)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    ('2020-01-01', '2020-01-01', False),
    ('2020-01-01', '2020-01-02', True),
    ('2020-01-01', '2020-01-32', False),
    ('2020-01-01', '2019-12-31', False)
])
def test_date_gt(comparison: str, value: str, expected: bool):
    r = cell.DateGT(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    ('2020-01-01', '2020-01-01', True),
    ('2020-01-01', '2020-01-02', True),
    ('2020-01-01', '2020-01-32', False),
    ('2020-01-01', '2019-12-31', False)
])
def test_date_gte(comparison: str, value: str, expected: bool):
    r = cell.DateGTE(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    ('2020-01-01', '2020-01-01', True),
    ('2020-01-01', '2020-01-02', False),
    ('2020-01-01', '2020-01-32', False),
    ('2020-01-01', '2019-12-31', False)
])
def test_date_et(comparison: str, value: str, expected: bool):
    r = cell.DateET(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    ('2020-01-01', '2020-01-01', True),
    ('2020-01-01', '2020-01-02', False),
    ('2020-01-01', '2020-01-32', False),
    ('2020-01-01', '2019-12-31', True)
])
def test_date_lte(comparison: str, value: str, expected: bool):
    r = cell.DateLTE(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('comparison,value,expected', [
    ('2020-01-01', '2020-01-01', False),
    ('2020-01-01', '2020-01-02', False),
    ('2020-01-01', '2020-01-32', False),
    ('2020-01-01', '2019-12-31', True)
])
def test_date_lt(comparison: str, value: str, expected: bool):
    r = cell.DateLT(comparison)
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('compared,data,expected', [
    ('x', ('1', {'x': '0'}), True),
    ('x', ('1', {'x': '1'}), False),
    ('z', ('1', {'x': '1', 'z': '0'}), True)
])
def test_greater_than_column(compared: str, data, expected: bool):
    r = cell.GreaterThanColumn(compared)
    assert r._evaluator()(*r._prepare(data)) is expected


@pytest.mark.parametrize('compared,data,expected', [
    ('x', ('1', {'x': '0'}), True),
    ('x', ('1', {'x': '1'}), True),
    ('x', ('1', {'x': '2'}), False),
    ('z', ('1', {'x': '1', 'z': '0'}), True)
])
def test_greater_than_or_equal_column(compared: str, data, expected: bool):
    r = cell.GreaterThanOrEqualColumn(compared)
    assert r._evaluator()(*r._prepare(data)) is expected


@pytest.mark.parametrize('compared,data,expected', [
    ('x', ('0', {'x': '1'}), True),
    ('x', ('1', {'x': '1'}), False),
    ('z', ('0', {'x': '0', 'z': '1'}), True)
])
def test_less_than_column(compared: str, data, expected: bool):
    r = cell.LessThanColumn(compared)
    assert r._evaluator()(*r._prepare(data)) is expected


@pytest.mark.parametrize('compared,data,expected', [
    ('x', ('0', {'x': '1'}), True),
    ('x', ('1', {'x': '1'}), True),
    ('x', ('2', {'x': '1'}), False),
    ('z', ('0', {'x': '0', 'z': '1'}), True)
])
def test_less_than_or_equal_column(compared: str, data, expected: bool):
    r = cell.LessThanOrEqualColumn(compared)
    assert r._evaluator()(*r._prepare(data)) is expected


@pytest.mark.parametrize('compare,row,expected', [
    ('col_b', ('', {'col_b': ''}), True),
    ('col_b', ('test', {'col_b': ''}), True),
    ('col_b', ('test', {'col_b': 'test'}), True),
    ('col_b', ('', {'col_b': 'test'}), False),
    (['col_b', 'col_c'], ('', {'col_b': '', 'col_c': ''}), True),
    (['col_b', 'col_c'], ('test', {'col_b': '', 'col_c': ''}), True),
    (['col_b', 'col_c'], ('test', {'col_b': '', 'col_c': 'test'}), True),
    (['col_b', 'col_c'], ('test', {'col_b': 'test', 'col_c': 'test'}), True),
    (['col_b', 'col_c'], ('', {'col_b': 'test', 'col_c': ''}), False),
    (['col_b', 'col_c'], ('', {'col_b': '', 'col_c': 'test'}), False),
    (['col_b', 'col_c'], ('', {'col_b': 'test', 'col_c': 'test'}), False)
])
def test_not_null_if_compare(compare, row, expected):
    r = cell.NotNullIfCompare(compare)
    assert r._evaluator()(*r._prepare(row)) is expected


@pytest.mark.parametrize('other,row,expected', [
    ('col_b', ('', {'col_b': ''}), True),
    ('col_b', ('', {'col_b': 'x'}), True),
    ('col_b', ('x', {'col_b': ''}), True),
    ('col_b', ('x', {'col_b': 'x'}), False),
])
def test_other_cant_exist(other, row, expected):
    r = cell.OtherCantExist(other)
    assert r._evaluator()(*r._prepare(row)) is expected


@pytest.mark.parametrize('other,row,expected', [
    ('col_b', ('', {'col_b': ''}), True),
    ('col_b', ('', {'col_b': 'x'}), True),
    ('col_b', ('x', {'col_b': ''}), False),
    ('col_b', ('x', {'col_b': 'x'}), True),
])
def test_other_must_exist(other, row, expected):
    r = cell.OtherMustExist(other)
    assert r._evaluator()(*r._prepare(row)) is expected


@pytest.mark.parametrize('row, other, values, expected', [
    (('1', {'c': 'x'}), 'c', 'x', True),
    (('', {'c': 'x'}), 'c', 'x', False),
    (('1', {'c': 'x'}), 'c', ['x'], True),
    (('1', {'c': 'y'}), 'c', ['y'], True),
    (('1', {'c': 'y'}), 'c', ['x', 'y'], True),
    (('', {'c': 'x'}), 'c', ['x'], False),
    (('', {'c': 'y'}), 'c', ['y'], False),
    (('', {'c': 'y'}), 'c', ['x', 'y'], False),
])
def test_other_must_exist_if_equals(row, other, values, expected):
    r = cell.NotNullIfOtherEquals(other, values)
    assert r._evaluator()(*r._prepare(row)) is expected


@pytest.mark.parametrize('value, expected', [
    ('1', True),
    ('1 1', True),
    ('1 ', False),
    ('1 ', False),
    (' 1 ', False),
    ('1\t', False),
])
def test_non_trim(value, expected):
    r = cell.NonTrim()
    assert r._evaluator()(*r._prepare(value)) is expected


@pytest.mark.parametrize('value, expected', [
    ('+3', True),
    ('3.2e23', False),
    ('-4.70e+9', False),
    ('-.2E-4', False),
    ('-7.6603', True),
    ('+0003 ', True),
    ('37.e88', False)
])
def test_non_scientific(value, expected):
    r = cell.NoScientific()
    assert r._evaluator()(*r._prepare(value)) is expected
