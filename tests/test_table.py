from pathlib import Path
from uuid import uuid4

import pytest
from openpyxl import Workbook

from rumydata.field import Integer, Field, Text
from rumydata.rules.column import Unique
from rumydata.table import Layout, CsvFile, ExcelFile, _BaseFile
from tests.utils import mock_no_module


@pytest.fixture
def wb_sheets(tmpdir):
    wb = Workbook()
    ws0 = wb.active
    ws0.append([''])
    ws1 = wb.create_sheet('wrong')
    ws1.append(['x'])
    ws1.append(['aa'])
    ws2 = wb.create_sheet('right')
    ws2.append(['x'])
    ws2.append(['a'])
    p = Path(tmpdir, f"{uuid4().hex}.xlsx")
    wb.save(p)
    yield p


def test_exception_message_structure(tmpdir):
    """
    Exception message structure

    This is a very hokey test to check the behavior of the exception message
    structure. This should be improved. This is going to break all the time as
    rule messages and various minor details get changed in the underlying
    classes.
    """
    hid = uuid4().hex[:5]
    p = Path(tmpdir, hid)
    p.write_text('\n'.join(["c1,c2", "1,23", "1,1"]))
    msg = [
        f" - File: {hid}",
        "   - Row: 2",
        "     - Cell: 2,2 (c2)",
        "       - MaxDigit: must have no more than 1 digit characters",
        "   - Column: 1 (c1)",
        "     - Unique: values must be unique",
    ]
    msg = '\n'.join(msg)
    lay = Layout({'c1': Integer(1, rules=[Unique()]), 'c2': Integer(1)})
    try:
        CsvFile(lay).check(p)
    except AssertionError as ae:
        print(ae)
        print(msg)
        assert str(ae).endswith(msg)


def test_documentation():
    """ An equally silly test of documentation output """
    layout = Layout({'x': Field()})
    expected = ' - **x**\n   - cannot be empty/blank'
    assert layout.documentation() == expected


@pytest.mark.parametrize('choice, valid', [
    ('md', True),
    ('html', True),
    ('yyz', False)
])
def test_documentation_types(choice, valid):
    layout = Layout({'x': Field()})
    if valid:
        assert isinstance(layout.documentation(doc_type=choice), str)
    else:
        with pytest.raises(TypeError):
            layout.documentation(doc_type=choice)


@pytest.mark.parametrize('choice, valid', [
    ('md', True),
    ('html', True),
    ('yyz', False)
])
@pytest.mark.parametrize('valid_file', [False, True])
def test_file_output_types(choice, valid, valid_file, tmpdir):
    layout = Layout({'x': Integer(1)})
    p = Path(tmpdir, 'test_file_output_types.csv')
    if valid_file:
        p.write_text('x\n1\n')
    else:
        p.write_text('x\nx\n')

    if valid:
        assert isinstance(CsvFile(layout).check(p, choice), str)
    else:
        with pytest.raises(TypeError):
            CsvFile(layout).check(p, choice)


def test_no_excel(mocker):
    mocker.patch('builtins.__import__', wraps=__import__, side_effect=mock_no_module('openpyxl'))
    with pytest.raises(ModuleNotFoundError):
        ExcelFile(Layout({'x': Integer(1)}))


def test_base_file_stubs():
    assert not _BaseFile(Layout({'x': Integer(1)}))._rows(Path('x'))


def test_excel_wrong_sheet(wb_sheets):
    lay = Layout({'x': Text(1)})
    with pytest.raises(AssertionError):
        ExcelFile(lay, sheet='wrong').check(wb_sheets)


def test_excel_right_sheet(wb_sheets):
    lay = Layout({'x': Text(1)})
    assert not ExcelFile(lay, sheet='right').check(wb_sheets)


def test_file_name_match(tmpdir):
    mock_file = Path(tmpdir, '12345_test_file_report.csv')
    pattern = r'\d{5}_\D*_\D*_report.csv'
    layout = Layout({'x': Integer(1)})
    mock_file.write_text('x\n1\n')
    assert not CsvFile(layout, file_name_pattern=pattern).check(mock_file)
