"""
This is a giant dumpster fire. It needs to be broken apart into a set of more
sensible scripts.
"""

import csv
import uuid
from pathlib import Path

import pytest
from openpyxl import Workbook

import rumydata.rules.cell
import rumydata.table
from rumydata import exception as ex
from rumydata import field
from rumydata.rules import column as cr, table as tr, header as hr
from rumydata.rules.cell import make_static_cell_rule
from rumydata.table import CsvFile, ExcelFile


def write_row(directory, columns: rumydata.table.Layout, row, rows=False):
    p = Path(directory, str(uuid.uuid4()))
    with p.open('w', newline='') as o:
        writer = csv.writer(o)
        writer.writerow(list(columns.layout))
        if rows:
            for r in row:
                writer.writerow(r)
        else:
            writer.writerow(row)
    return p


@pytest.fixture()
def basic_good(tmpdir):
    p = Path(tmpdir, 'good.csv')
    with p.open('w', newline='') as o:
        writer = csv.writer(o)
        writer.writerow(['col1', 'col2', 'col3', 'col4'])
        writer.writerow(['A', '1', '2020-01-01', 'X'])
    yield p.as_posix()


@pytest.fixture()
def basic_good_excel(tmpdir):
    p = Path(tmpdir, 'good.xlsx')
    wb = Workbook()
    ws = wb.active
    ws.append(['col1', 'col2', 'col3', 'col4'])
    ws.append(['A', '1', '2020-01-01', 'X'])
    wb.save(p)
    yield p.as_posix()


@pytest.fixture()
def basic_row_skip_good(tmpdir):
    p = Path(tmpdir, 'good.csv')
    with p.open('w', newline='') as o:
        writer = csv.writer(o)
        writer.writerow(['garbage'])
        writer.writerow(['garbage'])
        writer.writerow(['col1', 'col2', 'col3', 'col4'])
        writer.writerow(['A', '1', '2020-01-01', 'X'])
    yield p.as_posix()


@pytest.fixture()
def readme_layout():
    return {
        'col1': field.Text(8),
        'col2': field.Choice(['x', 'y', 'z'], nullable=True),
        'col3': field.Integer(1)
    }


@pytest.fixture()
def readme_data(tmpdir):
    p = Path(tmpdir, 'bobs_data.csv')
    p.write_text('\n'.join([
        "col1,col2,col3",
        "abc,x,-1",
        "def,,0",
        "ghi,a,1"
    ]))
    yield p.as_posix()


def empty_rows(rows, directory):
    p = Path(directory, str(uuid.uuid4()))
    with p.open('w') as f:
        w = csv.writer(f)
        w.writerow(['x'])
        for i in range(rows):
            w.writerow('')
    return p


def test_file_not_exists(basic):
    assert CsvFile(rumydata.table.Layout(basic)). \
        _has_error('abc123.csv', ex.FileError)


def test_file_good(basic_good, basic):
    assert not CsvFile(rumydata.table.Layout(basic)).check(basic_good)


def test_file_excel_good(basic_good_excel, basic):
    assert not ExcelFile(rumydata.table.Layout(basic)).check(basic_good_excel)


def test_file_invalid_type(basic):
    with pytest.raises(TypeError):
        CsvFile(rumydata.table.Layout(basic), file_type='xxx')


def test_file_row_skip_good(basic_row_skip_good, basic):
    assert not CsvFile(rumydata.table.Layout(basic), skip_rows=2).check(basic_row_skip_good)


def test_layout_good(basic, basic_good):
    assert not CsvFile(rumydata.table.Layout(basic)).check(basic_good)


def test_readme_example(readme_layout, readme_data):
    rex = rumydata.rules.cell.Choice.rule_exception()
    assert CsvFile(rumydata.table.Layout(readme_layout))._has_error(readme_data, rex)


@pytest.mark.parametrize('rows,me', [
    (1, 0),
    (2, 1),
    (101, 100),
    (int(1e5), 100),
])
def test_has_max_error(tmpdir, rows, me):
    fields = rumydata.table.Layout({'x': field.Field()})
    file = empty_rows(rows, tmpdir)
    assert CsvFile(fields, max_errors=me)._has_error(file, tr.MaxError.rule_exception())


@pytest.mark.parametrize('rows,me', [
    (1, 1),
    (99, 100),
    (100, 100),
    (100, int(1e5)),
])
def test_missing_max_error(tmpdir, rows, me):
    fields = rumydata.table.Layout({'x': field.Field()})
    file = empty_rows(rows, tmpdir)
    assert not CsvFile(fields, max_errors=me)._has_error(file, tr.MaxError.rule_exception())


def test_column_compare_row_good():
    fields = rumydata.table.Layout({
        'a': rumydata.field.Integer(1, rules=[rumydata.rules.cell.GreaterThanColumn('b')]),
        'b': rumydata.field.Integer(1)
    })
    assert not fields.check_row(['3', '2'])


@pytest.mark.parametrize('compare_rule,row', [
    (rumydata.rules.cell.GreaterThanColumn('x'), ['2', '3']),
])
def test_column_compare_file_good(tmpdir, compare_rule, row):
    cols = rumydata.table.Layout({'x': field.Field(), 'y': field.Field(rules=[compare_rule])})
    assert not CsvFile(cols).check(write_row(tmpdir, cols, row))


@pytest.mark.parametrize('compare_rule,row', [
    (rumydata.rules.cell.GreaterThanColumn('x'), ['1', '1']),
])
def test_column_compare_file_bad(tmpdir, compare_rule, row):
    cols = rumydata.table.Layout({'x': field.Field(), 'y': field.Field(rules=[compare_rule])})
    assert CsvFile(cols)._has_error(write_row(tmpdir, cols, row), compare_rule.rule_exception())


def test_header_file_bad(tmpdir):
    cols1 = rumydata.table.Layout({'x': field.Field()})
    cols2 = rumydata.table.Layout({'y': field.Field()})
    row = ['1']
    fp = write_row(tmpdir, cols2, row)
    assert CsvFile(cols1)._has_error(fp, hr.NoMissing.rule_exception())


def test_unique_bad(tmpdir):
    cols = rumydata.table.Layout({'x': field.Field(rules=[cr.Unique()])})
    f = write_row(tmpdir, cols, [['1'], ['1'], ['1']], rows=True)
    assert CsvFile(cols)._has_error(f, cr.Unique.rule_exception())


def test_unique_good(tmpdir):
    cols = rumydata.table.Layout({'x': field.Field(rules=[cr.Unique()])})
    f = write_row(tmpdir, cols, [['1'], ['2'], ['3']], rows=True)
    assert not CsvFile(cols).check(f)


@pytest.mark.parametrize('row,kwargs', [
    (['1', '1'], {}),
    (['1', '1'], dict(empty_row_ok=False)),
    (['', ''], dict(empty_row_ok=True))
])
def test_empty_row_good(row, kwargs):
    lay = rumydata.table.Layout({'x': field.Integer(1), 'y': field.Integer(2)}, **kwargs)
    assert not lay.check_row(row)


def test_empty_row_file_good(tmpdir):
    cols = rumydata.table.Layout({'x': field.Field()}, empty_row_ok=True)
    f = write_row(tmpdir, cols, [['1'], ['2'], ['']], rows=True)
    assert not CsvFile(cols).check(f)


@pytest.mark.parametrize('row', [
    (['1', '']),
    (['', '']),
    (['1', '1'])
])
def test_ignore_row(row):
    """ Test that ignore rows count as empty for the purpose of accepting empty rows """
    lay = rumydata.table.Layout(
        {'x': field.Ignore(), 'y': field.Integer(1)}, empty_row_ok=True
    )
    assert not lay.check_row(row)


def test_debug_mode_pre_process(mocker):
    """ Debug messages should only appear when debug method has been patched """
    try:
        # noinspection PyTypeChecker
        field.Date().check_cell(None)
    except AssertionError as ae:
        assert '[DEBUG]' not in str(ae)

    mocker.patch('rumydata.exception.debug', return_value=True)
    try:
        # noinspection PyTypeChecker
        field.Date().check_cell(None)
    except AssertionError as ae:
        assert '[DEBUG]' in str(ae)


def test_debug_mode(mocker):
    """ Debug messages should only appear when debug method has been patched """

    r = make_static_cell_rule(lambda x: 1 / 0, 'raise an exception')
    try:
        # noinspection PyTypeChecker
        field.Field(rules=[r]).check_cell('1')
    except AssertionError as ae:
        assert '[DEBUG]' not in str(ae)

    mocker.patch('rumydata.exception.debug', return_value=True)
    try:
        # noinspection PyTypeChecker
        field.Field(rules=[r]).check_cell('1')
    except AssertionError as ae:
        assert '[DEBUG]' in str(ae)


def test_cell_trim():
    assert not field.Choice(['x'], strip=True).check_cell(' x ')


def test_column_trim():
    assert not field.Choice(['x'], strip=True).check_column([' x '])
