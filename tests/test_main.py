import pytest

from rumydata import *
from rumydata.exception import *
from rumydata.component import DataDefinition


@pytest.fixture()
def basic() -> dict:
    return {'col1': Text(1), 'col2': Integer(1), 'col3': Date()}


def includes_error(error_list, expected_error):
    return any([isinstance(x, expected_error) for x in error_list])


def test_file_not_exists(basic):
    with pytest.raises(FileNotFoundError):
        File('abc123.csv', DataDefinition('abc123.csv', basic))


def test_text():
    assert not Text(1).check_errors('x')
    assert not Text(2).check_errors('x')

    assert includes_error(Text(2).check_errors('xxx'), DataLengthError)
    assert includes_error(Text(max_length=80, min_length=1).check_errors(''), DataLengthError)


def test_date():
    assert not Date().check_errors('20200101')

    assert includes_error(Date().check_errors('2020'), DateFormatError)
    assert includes_error(Date().check_errors('20200101 '), DateFormatError)
    assert includes_error(Date().check_errors('2020-01-01'), DateFormatError)
    assert includes_error(Date().check_errors('99999999'), ValueError)


def test_currency():
    assert not Currency(5).check_errors('123.45')
    assert not Currency(5).check_errors('123.00')
    assert not Currency(5).check_errors('123.0')
    assert not Currency(5).check_errors('123')

    assert includes_error(Currency(4).check_errors('123.45'), DataLengthError)
    assert includes_error(Currency(4).check_errors('123.'), CurrencyPatternError)
    assert includes_error(Currency(6).check_errors('123.456'), CurrencyPatternError)


def test_integer():
    assert not Integer(1).check_errors('0')
    assert not Integer(1).check_errors('1')
    assert not Integer(2).check_errors('1')
    assert not Integer(2, min_length=1).check_errors('1')

    assert includes_error(Integer(2, min_length=2).check_errors('1'), DataLengthError)
    assert includes_error(Integer(2).check_errors('111'), DataLengthError)
    assert includes_error(Integer(2).check_errors('00'), LeadingZeroError)
    assert includes_error(Integer(2).check_errors('01'), LeadingZeroError)


def test_choice():
    assert not Choice(['x']).check_errors('x')
    assert not Choice(['x', 'y']).check_errors('x')
    assert not Choice(['x', 'y']).check_errors('y')

    assert includes_error(Choice(['x']).check_errors('z'), InvalidChoiceError)


def test_row(basic):
    assert not Row(basic).check_errors([1, 2, 3])

    assert includes_error(Row(basic).check_errors([1, 2, 3, 4]), TooManyFieldsError)
    assert includes_error(Row(basic).check_errors([1, 2]), NotEnoughFieldsError)


def test_header(basic):
    assert not Header(basic).check_errors(['col1', 'col2', 'col3'])

    assert includes_error(Header(basic).check_errors(['col1', 'col2']), MissingColumnError)
    assert includes_error(Header(basic).check_errors(['col1', 'col2', 'col2']), DuplicateColumnError)
    assert includes_error(Header(basic).check_errors(['col1', 'col2', 'col4']), UnexpectedColumnError)
