import pytest

from rumydata.exception import *
from rumydata.validation import Layout
from rumydata.cell import *


@pytest.fixture()
def basic() -> dict:
    return {'col1': Text(1), 'col2': Integer(1), 'col3': Date()}


@pytest.fixture()
def basic_definition(basic):
    return Layout(basic, pattern=r'good\.csv')


@pytest.fixture()
def basic_good():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, 'good.csv')
        with p.open('w') as o:
            writer = csv.writer(o)
            writer.writerow(['col1', 'col2', 'col3'])
            writer.writerow(['A', 1, '2020-01-01'])
        yield p.as_posix()


@pytest.fixture()
def readme_layout():
    return {
        'col1': Text(8),
        'col2': Choice(['x', 'y', 'z'], nullable=True),
        'col3': Integer(1)
    }


@pytest.fixture()
def readme_data():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, 'bobs_data.csv')
        p.write_text('\n'.join([
            "col1,col2,col3",
            "abc,x,-1",
            "def,,0",
            "ghi,a,1"
        ]))
        yield p.as_posix()


def includes_error(error_list, expected_error):
    return any([isinstance(x, expected_error) for x in error_list])


def test_file_not_exists(basic):
    assert includes_error(
        File(Layout(basic, pattern='abc123.csv')).__check__('abc123.csv'),
        FileNotFoundError
    )


@pytest.mark.parametrize('value,kwargs', [
    ('x', dict(max_length=1)),
    ('x', dict(max_length=2)),
    ('', dict(max_length=1, nullable=True)),
    ('', dict(max_length=1, min_length=1, nullable=True))
])
def test_text_good(value, kwargs):
    assert not Text(**kwargs).__check__(value)


@pytest.mark.parametrize('value,kwargs,err', [
    ('', dict(max_length=1), NullValueError),
    ('xxx', dict(max_length=2), DataLengthError),
    ('x', dict(max_length=80, min_length=2), DataLengthError),
])
def test_text_bad(value, kwargs, err):
    assert includes_error(Text(**kwargs).__check__(value), err)


@pytest.mark.parametrize('value,kwargs', [
    ('2020-01-01', {}),
    ('', dict(nullable=True))
])
def test_date_good(value, kwargs):
    assert not Date(**kwargs).__check__(value)


@pytest.mark.parametrize('value,err', [
    ('', NullValueError),
    ('20200101', ValueError),
    ('9999-99-99', ValueError)
])
def test_date_bad(value, err):
    assert includes_error(Date().__check__(value), err)


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
    assert not Currency(sig_dig, **kwargs).__check__(value)


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
    assert includes_error(Currency(sig_dig, rules=rules).__check__(value), err)


@pytest.mark.parametrize('value,max_length', [
    ('1', 3),
    ('12', 3),
    ('123', 3)
])
def test_digit_good(value, max_length):
    assert not Digit(max_length).__check__(value)


@pytest.mark.parametrize('value,max_length,err', [
    ('-123', 3, DataError),
    ('-123', 3, DataLengthError)
])
def test_digit_bad(value, max_length, err):
    assert includes_error(Digit(max_length).__check__(value), err)


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
    assert not Integer(max_length, **kwargs).__check__(value)


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
    assert includes_error(Integer(max_length, **kwargs).__check__(value), err)


@pytest.mark.parametrize('value,choices,kwargs', [
    ('x', ['x'], {}),
    ('x', ['x', 'y'], {}),
    ('y', ['x', 'y'], {}),
    ('', ['x'], dict(nullable=True))
])
def test_choice_good(value, choices, kwargs):
    assert not Choice(choices, **kwargs).__check__(value)


@pytest.mark.parametrize('value,choices,kwargs,err', [
    ('', ['x'], {}, NullValueError),
    ('x', ['z'], {}, InvalidChoiceError)
])
def test_choice_bad(value, choices, kwargs, err):
    assert includes_error(Choice(choices, **kwargs).__check__(value), err)


def test_row_good(basic):
    assert not Row(basic).__check__([1, 2, 3])


@pytest.mark.parametrize('value,err', [
    ([1, 2, 3, 4], ValueComparisonError),
    ([1, 2], ValueComparisonError)
])
def test_row_bad(basic, value, err):
    assert includes_error(Row(basic).__check__(value), err)


def test_header_good(basic):
    assert not Header(basic).__check__(['col1', 'col2', 'col3'])


@pytest.mark.parametrize('value,err', [
    (['col1', 'col2'], MissingColumnError),
    (['col1', 'col2', 'col2'], DuplicateColumnError),
    (['col1', 'col2', 'col4'], UnexpectedColumnError)
])
def test_header_bad(basic, value, err):
    assert includes_error(Header(basic).__check__(value), err)


def test_file_good(basic_good, basic_definition):
    assert not File(basic_definition).__check__(basic_good)


def test_layout_good(basic, basic_good):
    assert not Layout(basic).check_file(basic_good)


def test_readme_example(readme_layout, readme_data):
    assert includes_error(
        Layout(readme_layout).check_file(readme_data), InvalidChoiceError
    )
