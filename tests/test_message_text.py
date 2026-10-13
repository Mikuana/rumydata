"""
Message/digest text pinning for the refactored shared code paths

The compactness refactor replaced per-class message assembly with shared bases
and small helpers (rules.cell.Comparison, rules.row._LengthComparison,
exception._label/_md/_append, field._register_numeric). The rule-evaluator
truth tables already exist in test_rules_*; these tests pin the exact
user-visible *text* produced by those paths (explanations, exception strings,
descriptors, digests, documentation) so a future refactor cannot drift the
frozen message surface silently.
"""
from pathlib import Path

import pytest

import rumydata.exception as ex
import rumydata.field as field
import rumydata.rules.cell as cell
import rumydata.rules.column as column
import rumydata.rules.header as header
import rumydata.rules.row as row
import rumydata.rules.table as table
from rumydata.table import Layout, CsvFile


# noinspection DuplicatedCode
@pytest.mark.parametrize('rule_cls,args,expected', [
    (cell.NotNull, (), 'cannot be empty/blank'),
    (cell.ExactChar, (3,), 'must be exactly 3 characters'),
    (cell.MinChar, (3,), 'must be at least 3 characters'),
    (cell.MaxChar, (3,), 'must be no more than 3 characters'),
    (cell.AsciiChar, (), 'must have only ASCII characters'),
    (cell.NonTrim, (), 'Value has trailing or leading whitespace'),
    (cell.MinDigit, (3,), 'must have at least 3 digit characters'),
    (cell.MaxDigit, (3,), 'must have no more than 3 digit characters'),
    (cell.OnlyNumbers, (), 'must only contain characters 0-9'),
    (cell.NoLeadingZero, (), 'cannot have a leading zero digit'),
    (cell.NoScientific, (), 'cannot have scientific notation'),
    (cell.CanBeFloat, (), 'can be coerced into a float value'),
    (cell.CanBeInteger, (), 'can be coerced into an integer value'),
    (cell.NumericDecimals, (3,), 'cannot have more than 3 digits after the decimal point'),
])
def test_cell_explain(rule_cls, args, expected):
    assert rule_cls(*args)._explain() == expected


@pytest.mark.parametrize('rule_cls,value,expected', [
    (cell.LengthGT, 5, 'greater than 5'),
    (cell.LengthGTE, 5, 'greater than or equal to 5'),
    (cell.LengthET, 5, 'equal to 5'),
    (cell.LengthLTE, 5, 'less than or equal to 5'),
    (cell.LengthLT, 5, 'less than 5'),
    (cell.NumericGT, 5, 'greater than 5'),
    (cell.NumericGTE, 5, 'greater than or equal to 5'),
    (cell.NumericET, 5, 'equal to 5'),
    (cell.NumericLTE, 5, 'less than or equal to 5'),
    (cell.NumericLT, 5, 'less than 5'),
])
def test_cell_comparison_explain(rule_cls, value, expected):
    """ The shared Comparison base assembles the family explain strings """
    assert rule_cls(value)._explain() == expected


@pytest.mark.parametrize('rule_cls,value,expected', [
    (cell.DateGT, '2020-01-01', 'greater than 2020-01-01 00:00:00'),
    (cell.DateGTE, '2020-01-01', 'greater than or equal to 2020-01-01 00:00:00'),
    (cell.DateET, '2020-01-01', 'equal to 2020-01-01 00:00:00'),
    (cell.DateLTE, '2021-01-01', 'less than or equal to 2021-01-01 00:00:00'),
    (cell.DateLT, '2021-01-01', 'less than 2021-01-01 00:00:00'),
])
def test_date_comparison_explain(rule_cls, value, expected):
    """ comparison_value is stored as a datetime, and str()'d in the explain """
    assert rule_cls(value)._explain() == expected


@pytest.mark.parametrize('rule_cls,args,expected', [
    (cell.GreaterThanColumn, ('y',), "must be greater than column 'y'"),
    (cell.GreaterThanOrEqualColumn, ('y',), "must be greater than or equal to column 'y'"),
    (cell.LessThanColumn, ('y',), "must be less than column 'y'"),
    (cell.LessThanOrEqualColumn, ('y',), "must be less than or equal to column 'y'"),
    (cell.OtherCantExist, ('y',), "cannot contain a value if 'y' is populated"),
    (cell.OtherMustExist, ('y',), "must contain a value if 'y' is populated"),
    (cell.NotNullIfCompare, ('x',), "cannot be blank if 'x' contains a value"),
    (cell.NotNullIfCompare, (['a', 'b'],), "cannot be blank if 'a' or 'b' contains a value"),
    (cell.NotNullIfOtherEquals, ('x', 'a'), "cannot be blank if 'x' contains value: ['a']"),
    (cell.NotNullIfOtherEquals, ('x', ['a', 'b']), "cannot be blank if 'x' contains value: ['a', 'b']"),
])
def test_column_comparison_explain(rule_cls, args, expected):
    assert rule_cls(*args)._explain() == expected


def test_choice_explain():
    assert cell.Choice(['a', 'b'])._explain() == "must be one of ['a', 'b'] (case sensitive)"
    assert cell.Choice(['a', 'b'], case_insensitive=True)._explain() == (
        "must be one of ['a', 'b'] (case insensitive)"
    )


@pytest.mark.parametrize('rule_cls,n,expected', [
    (row.RowLengthLTE, 3, 'row length must be equal to 3, not greater'),
    (row.RowLengthGTE, 3, 'row length must be equal to 3, not less'),
])
def test_row_length_explain(rule_cls, n, expected):
    assert rule_cls(n)._explain() == expected


def test_row_length_evaluator():
    lte = row.RowLengthLTE(2)
    gte = row.RowLengthGTE(2)
    assert lte._evaluator()(*lte._prepare(['a', 'b'])) is True
    assert lte._evaluator()(*lte._prepare(['a', 'b', 'c'])) is False
    assert gte._evaluator()(*gte._prepare(['a', 'b'])) is True
    assert gte._evaluator()(*gte._prepare(['a'])) is False


def test_abstract_row_length_base_fails_closed():
    """ The shared base is not a Rule; documented to fail closed until combined """
    base = row._LengthComparison(3)
    assert base._evaluator()(['a']) is False
    assert base._explain() == 'row length must be equal to 3, not N/A'


def test_abstract_cell_comparison_base_fails_closed():
    """ The shared base is not a Rule; documented to fail closed until combined """
    base = cell.Comparison(5)
    assert base._evaluator()('x') is False
    assert base._measure('x') == 'x'
    assert base._explain() == 'N/A 5'


@pytest.mark.parametrize('rule_cls,expected', [
    (header.NoExtra, 'Header row must not have unexpected columns'),
    (header.NoMissing, 'Header row must not be missing any expected columns'),
    (header.NoDuplicate, 'Header row must not contain duplicate values'),
    (header.ColumnOrder, 'Header row must explicitly match order of definition'),
])
def test_header_explain(rule_cls, expected):
    assert rule_cls(Layout({'a': field.Text(5)}))._explain() == expected


def test_header_prepare_filters_empty_columns():
    lay = Layout({'a': field.Text(5)}, empty_cols_ok=True)
    assert header.NoExtra(lay)._prepare(['a', '', 'b']) == (['a', 'b'],)
    lay = Layout({'a': field.Text(5)})
    assert header.NoExtra(lay)._prepare(['a', '', 'b']) == (['a', '', 'b'],)


def test_unique_explain_and_blank_filter():
    r = column.Unique()
    assert r._explain() == 'values must be unique'
    assert r._prepare(['a', '', 'b', '']) == (['a', 'b'],)


@pytest.mark.parametrize('rule_cls,args,expected', [
    (table.FileExists, (), 'files must exist'),
    (table.FileNameMatch, ('^x.*$',), 'file must match naming pattern ^x.*$'),
    # note: the MaxError wording is a pre-existing quirk, pinned as-is
    (table.MaxError, (100,), 'files returned row errors than allowed: 100'),
])
def test_table_rule_explain(rule_cls, args, expected):
    assert rule_cls(*args)._explain() == expected


def test_exception_str_format():
    assert str(ex.CellError(index=0, rix=0)) == '\n - Cell: 1,1'
    assert str(ex.CellError(index=0, rix=0, name='x')) == '\n - Cell: 1,1 (x)'
    assert str(ex.CellError(index=0, rix=0, zero_index=True)) == '\n - Cell: 0,0'
    assert str(ex.RowError(index=0)) == '\n - Row: 1'
    assert str(ex.RowError(index=0, zero_index=True)) == '\n - Row: 0'
    assert str(ex.ColumnError(index=0, name='x', zero_index=True)) == '\n - Column: 0 (x)'
    assert str(ex.FileError(file='f.csv')) == '\n - File: f.csv'
    assert str(ex.FileError(file='f.csv', msg='boom')) == '\n - File: f.csv; boom'
    assert str(ex.CustomError('custom text')) == '\n - custom text'


def test_exception_excel_cell_format():
    assert str(ex.CellError(index=0, rix=0, use_excel_cell_format=True)) == '\n - Cell: A1'
    assert str(ex.CellError(index=26, rix=0, use_excel_cell_format=True)) == '\n - Cell: AA1'


def test_nested_exception_str():
    """ The _label/_md refactoring must preserve the full nested tree text """
    cell_err = ex.CellError(index=0, rix=0, name='x',
                            errors=[cell.NotNull().rule_exception()('cannot be empty/blank')])
    row_err = ex.RowError(index=0, errors=[cell_err])
    file_err = ex.FileError(file='f.csv', errors=[row_err])
    assert str(file_err) == (
        '\n - File: f.csv\n'
        '   - Row: 1\n'
        '     - Cell: 1,1 (x)\n'
        '       - NotNull: cannot be empty/blank'
    )


@pytest.mark.parametrize('factory,expected', [
    (lambda: field.Text(10), {'Type': 'String', 'Max Length': '10 characters'}),
    (lambda: field.Text(10, min_length=2),
     {'Type': 'String', 'Max Length': '10 characters', 'Min Length': '2 characters'}),
    (lambda: field.Digit(4, min_length=2),
     {'Type': 'Numeric', 'Format': '0000', 'Max Length': '4 digits', 'Min Length': '2 digits'}),
    # Integer/Number intentionally reuse max_length in 'Min Length' (preserved quirk)
    (lambda: field.Integer(4, min_length=2),
     {'Type': 'Numeric', 'Format': '9999', 'Max Length': '4 digits', 'Min Length': '4 digits'}),
    (lambda: field.Number(4, min_length=2),
     {'Type': 'Numeric', 'Format': '9999.0', 'Max Length': '4 digits', 'Min Length': '4 digits'}),
    (lambda: field.Number(4, allow_scientific=True),
     {'Type': 'Numeric', 'Format': '9999.0', 'Max Length': '4 digits'}),
    (lambda: field.Currency(5), {'Type': 'Numeric', 'Format': '999.99', 'Max Length': '5 digits'}),
    (lambda: field.Date(min_date='2020-01-01', max_date='2021-01-01'),
     {'Type': 'Date', 'Format': 'YYYY-MM-DD', 'Max Date': '2021-01-01', 'Min Date': '2020-01-01'}),
    (lambda: field.Choice(['a', 'b'], case_insensitive=True), {'Type': 'Choice', 'Choices': 'a,b'}),
    (lambda: field.Empty(), {}),
    (lambda: field.Ignore(), {}),
])
def test_field_descriptors(factory, expected):
    assert factory().descriptors == expected


def test_integer_digest_order():
    """ Descriptor and rule explain order is part of the documented output """
    assert field.Integer(4, min_length=2)._digest() == [
        'Type: Numeric', 'Format: 9999', 'Max Length: 4 digits', 'Min Length: '
        '4 digits', 'cannot be empty/blank', 'can be coerced into an integer value',
        'cannot have a leading zero digit', 'must have no more than 4 digit characters',
        'must have at least 2 digit characters'
    ]


def test_text_digest_nullable():
    assert field.Text(10, min_length=2, nullable=True)._digest() == [
        'Type: String', 'Max Length: 10 characters', 'Min Length: 2 characters',
        'must be no more than 10 characters', 'must be at least 2 characters', 'Nullable'
    ]


def test_empty_ignore_digest():
    assert field.Empty()._digest() == ['must be no more than 0 characters', 'Nullable']
    assert field.Ignore()._digest() == ['Nullable']


def test_layout_documentation_md():
    lay = Layout({'x': field.Integer(1)})
    assert lay.documentation() == (
        ' - **x**\n'
        '   - Type: Numeric\n'
        '   - Format: 9\n'
        '   - Max Length: 1 digits\n'
        '   - cannot be empty/blank\n'
        '   - can be coerced into an integer value\n'
        '   - cannot have a leading zero digit\n'
        '   - must have no more than 1 digit characters'
    )


@pytest.mark.xfail(
    reason='bug-001: documented `title` param always raised TypeError in '
    'Layout.__init__ (pre-existing on main, not a refactor regression); '
    'see .dev-orchestrator/001-compact-legibility/qa/bugs.md',
    strict=False,
)
def test_layout_title_in_documentation():
    """ The documented `title` parameter should appear as the digest header """
    lay = Layout({'x': field.Integer(1)}, title='My Table')
    assert lay.documentation().startswith('# My Table\n\n')


def test_file_check_error_message(tmpdir):
    """ Full nested tree of a failing file check, as reported by `check` """
    p = Path(tmpdir, 'f.csv')
    p.write_text('x\nabc\n')
    lay = Layout({'x': field.Integer(1)})
    with pytest.raises(AssertionError) as ei:
        CsvFile(lay).check(p)
    assert str(ei.value) == (
        '\n - File: f.csv\n'
        '   - Row: 2\n'
        '     - Cell: 2,1 (x)\n'
        '       - CanBeInteger: can be coerced into an integer value\n'
        '       - NoLeadingZero: cannot have a leading zero digit'
    )


def test_file_check_success_message(tmpdir):
    """ `check` with a doc_type returns the success message (always truthy) """
    p = Path(tmpdir, 'g.csv')
    p.write_text('x\n1\n')
    lay = Layout({'x': field.Integer(1)})
    assert CsvFile(lay).check(p, doc_type='md') == f'Validated file successfully: {p.as_posix()}'
