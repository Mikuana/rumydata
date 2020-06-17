import csv
import tempfile
from pathlib import Path

import pytest

from rumydata import *
from rumydata import rule
from rumydata.component import DataDefinition
from rumydata.exception import *


@pytest.fixture()
def basic() -> dict:
    return {'col1': Text(1), 'col2': Integer(1), 'col3': Date()}


@pytest.fixture()
def basic_definition(basic):
    return DataDefinition(r'good\.csv', basic)


@pytest.fixture()
def basic_good():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, 'good.csv')
        with p.open('w') as o:
            writer = csv.writer(o)
            writer.writerow(['col1', 'col2', 'col3'])
            writer.writerow(['A', 1, '2020-01-01'])
        yield p.as_posix()


def includes_error(error_list, expected_error):
    return any([isinstance(x, expected_error) for x in error_list])


def test_file_not_exists(basic):
    with pytest.raises(FileNotFoundError):
        File('abc123.csv', DataDefinition('abc123.csv', basic))


@pytest.mark.parametrize('value,kwargs', [
    ('x', dict(max_length=1)),
    ('x', dict(max_length=2)),
    ('', dict(max_length=1, nullable=True)),
    ('', dict(max_length=1, min_length=1, nullable=True))
])
def test_text_good(value, kwargs):
    assert not Text(**kwargs).check_rules(value)


@pytest.mark.parametrize('value,kwargs,err', [
    ('', dict(max_length=1), NullValueError),
    ('xxx', dict(max_length=2), DataLengthError),
    ('x', dict(max_length=80, min_length=2), DataLengthError),
])
def test_text_bad(value, kwargs, err):
    assert includes_error(Text(**kwargs).check_rules(value), err)


@pytest.mark.parametrize('value,kwargs', [
    ('2020-01-01', {}),
    ('', dict(nullable=True))
])
def test_date_good(value, kwargs):
    assert not Date(**kwargs).check_rules(value)


@pytest.mark.parametrize('value,err', [
    ('', NullValueError),
    ('20200101', ValueError),
    ('9999-99-99', ValueError)
])
def test_date_bad(value, err):
    assert includes_error(Date().check_rules(value), err)


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
    assert not Currency(sig_dig, **kwargs).check_rules(value)


@pytest.mark.parametrize('value,sig_dig,rules,err', [
    ('0.00', 5, [rule.NumericLT(0)], ValueComparisonError),
    ('0.01', 5, [rule.NumericLTE(0)], ValueComparisonError),
    ('0.01', 5, [rule.NumericET(0)], ValueComparisonError),
    ('-0.01', 5, [rule.NumericGTE(0)], ValueComparisonError),
    ('-0.01', 5, [rule.NumericGT(0)], ValueComparisonError),
    ('', 5, [], NullValueError),
    ('123.45', 4, [], DataLengthError),
    ('123.', 4, [], CurrencyPatternError),
    ('123.456', 4, [], CurrencyPatternError)
])
def test_currency_bad(value, sig_dig, rules, err):
    assert includes_error(Currency(sig_dig, rules=rules).check_rules(value), err)


@pytest.mark.parametrize('value,max_length', [
    ('1', 3),
    ('12', 3),
    ('123', 3)
])
def test_digit_good(value, max_length):
    assert not Digit(max_length).check_rules(value)


@pytest.mark.parametrize('value,max_length,err', [
    ('-123', 3, DataError),
    ('-123', 3, DataLengthError)
])
def test_digit_bad(value, max_length, err):
    assert includes_error(Digit(max_length).check_rules(value), err)


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
    assert not Integer(max_length, **kwargs).check_rules(value)


@pytest.mark.parametrize('value,max_length,kwargs,err', [
    ('0', 1, dict(rules=[rule.NumericLT(0)]), ValueComparisonError),
    ('1', 1, dict(rules=[rule.NumericLTE(0)]), ValueComparisonError),
    ('1', 1, dict(rules=[rule.NumericET(0)]), ValueComparisonError),
    ('-1', 1, dict(rules=[rule.NumericGTE(0)]), ValueComparisonError),
    ('0', 1, dict(rules=[rule.NumericGT(0)]), ValueComparisonError),
    ('', 1, {}, NullValueError),
    ('1', 2, dict(min_length=2), DataLengthError),
    ('111', 2, {}, DataLengthError),
    ('00', 2, {}, LeadingZeroError),
    ('01', 2, {}, LeadingZeroError)
])
def test_integer_bad(value, max_length, kwargs, err):
    assert includes_error(Integer(max_length, **kwargs).check_rules(value), err)


@pytest.mark.parametrize('value,choices,kwargs', [
    ('x', ['x'], {}),
    ('x', ['x', 'y'], {}),
    ('y', ['x', 'y'], {}),
    ('', ['x'], dict(nullable=True))
])
def test_choice_good(value, choices, kwargs):
    assert not Choice(choices, **kwargs).check_rules(value)


@pytest.mark.parametrize('value,choices,kwargs,err', [
    ('', ['x'], {}, NullValueError),
    ('x', ['z'], {}, InvalidChoiceError)
])
def test_choice_bad(value, choices, kwargs, err):
    assert includes_error(Choice(choices, **kwargs).check_rules(value), err)


def test_row_good(basic):
    assert not Row(basic).check_rules([1, 2, 3])


@pytest.mark.parametrize('value,err', [
    ([1, 2, 3, 4], ValueComparisonError),
    ([1, 2], ValueComparisonError)
])
def test_row_bad(basic, value, err):
    assert includes_error(Row(basic).check_rules(value), err)


def test_header_good(basic):
    assert not Header(basic).check_rules(['col1', 'col2', 'col3'])


@pytest.mark.parametrize('value,err', [
    (['col1', 'col2'], MissingColumnError),
    (['col1', 'col2', 'col2'], DuplicateColumnError),
    (['col1', 'col2', 'col4'], UnexpectedColumnError)
])
def test_header_bad(basic, value, err):
    assert includes_error(Header(basic).check_rules(value), err)


def test_file_good(basic_good, basic_definition):
    assert not File(basic_good, [basic_definition]).summary()
