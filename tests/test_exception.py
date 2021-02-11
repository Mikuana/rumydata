import pytest

import rumydata.exception as ex


@pytest.mark.parametrize('index,rix,zero_index,expected,assertion', [
    (1, 1, True, 'A1', True),
    (0, 0, False, 'A1', True),
    (1, 1, False, 'A1', False),
    (0, 0, True, 'A1', False),
    (1234, 50, True, 'AUL50', True),
    (1233, 49, False, 'AUL50', True),
    (1234, 50, False, 'AUL50', False),
    (1233, 49, True, 'AUL50', False),
    (16384, 2375201, True, 'XFD2375201', True),
    (16383, 2375200, False, 'XFD2375201', True),
    (16384, 2375201, False, 'XFD2375201', False),
    (16383, 2375200, True, 'XFD2375201', False),
])
def test_cell_error_excel_format(index, rix, zero_index, expected, assertion):
    x = str(ex.CellError(index, use_excel_cell_format=True, rix=rix, zero_index=zero_index))
    assert (expected in x) is assertion


def test_populated_custom_error():
    assert ex.CustomError('Testing')._md() != ' - None'


def test_custom_error():
    x = ex.CustomError('Testing')
    x._errors = [ex.CellError(0)]
    print(x._md())
    assert x._md() == " - Testing\n   - Cell: 1"
