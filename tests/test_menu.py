from pathlib import Path
from uuid import uuid4

import pytest

from rumydata.field import Integer
from rumydata.menu import menu
from rumydata.table import Layout
from tests.utils import mock_no_module


# noinspection DuplicatedCode
@pytest.mark.parametrize('choice', ['0', 'View Documentation'])
@pytest.mark.parametrize('no_md,ext', [(False, 'html'), (True, 'md')])
def test_view_documentation(choice, ext, no_md, mocker):
    """
    View Documentation option opens a browser with generated documentation. When
    the markdown module is available, this is shown in HTML, otherwise displayed
    as a raw .md text file.
    """
    if no_md:
        mocker.patch(
            'builtins.__import__', wraps=__import__, side_effect=mock_no_module('markdown')
        )

    mocker.patch('webbrowser.open')
    mocker.patch('builtins.print')
    mocker.patch('builtins.input', return_value=choice)

    expected = dict(extension=ext, output='open')
    ret = menu(Layout({'x': Integer(1)}))
    for k, v in expected.items():
        assert ret[k] == v


# noinspection DuplicatedCode
@pytest.mark.parametrize('choice', ['2', 'View Validation'])
@pytest.mark.parametrize('no_md,ext', [(False, 'html'), (True, 'md')])
@pytest.mark.parametrize('valid_file', [False, True])
def test_view_validation(choice, ext, no_md, valid_file, tmpdir, mocker):
    """
    View Validation option opens a browser with generated documentation. When
    the markdown module is available, this is shown in HTML, otherwise displayed
    as a raw .md text file.
    """
    if no_md:
        mocker.patch(
            'builtins.__import__', wraps=__import__, side_effect=mock_no_module('markdown')
        )
    if valid_file:
        p = Path(tmpdir, 'file.csv')
        p.write_text('x\n1\n')
        choice = (choice, p.as_posix())
        print(choice)
    else:
        choice = (choice, 'file.csv')

    mocker.patch('webbrowser.open')
    mocker.patch('builtins.print')
    mocker.patch('builtins.input', side_effect=choice)

    expected = dict(extension=ext, output='open')
    ret = menu(Layout({'x': Integer(1)}))
    for k, v in expected.items():
        assert ret[k] == v


@pytest.mark.parametrize('no_md', [False, True])
@pytest.mark.parametrize('choice,expected', [
    (['1', '0', '0'], dict(extension='md')),
    (['Generate Documentation', 'markdown', 'print'], dict(extension='md')),
    (['Generate Documentation', 'html', 'print'], dict(extension='html')),
    (['3', '0', 'x', '0'], dict(extension='md')),
    (['Generate Validation', 'markdown', 'x', 'print'], dict(extension='md')),
    (['Generate Validation', 'html', 'x', 'print'], dict(extension='html')),
])
def test_generate_print(choice, expected: dict, no_md, mocker):
    if no_md:
        mocker.patch(
            'builtins.__import__', wraps=__import__, side_effect=mock_no_module('markdown')
        )
        expected['extension'] = 'md'

    mocker.patch('webbrowser.open')
    mocker.patch('builtins.print')
    mocker.patch('builtins.input', side_effect=choice)

    expected['output'] = 'print'

    ret = menu(Layout({'x': Integer(1)}))
    for k, v in expected.items():
        assert ret[k] == v


@pytest.mark.parametrize('no_md', [False, True])
@pytest.mark.parametrize('choice,expected', [
    (['1', '0', '2'], dict(extension='md')),
    (['Generate Documentation', 'markdown', 'save'], dict(extension='md')),
    (['Generate Documentation', 'html', 'save'], dict(extension='html')),
    (['3', '0', 'x', '2'], dict(extension='md')),
    (['Generate Validation', 'markdown', 'x', 'save'], dict(extension='md')),
    (['Generate Validation', 'html', 'x', 'save'], dict(extension='html')),
])
def test_generate_save(choice, expected: dict, no_md, tmpdir, mocker):
    if no_md:
        mocker.patch(
            'builtins.__import__', wraps=__import__, side_effect=mock_no_module('markdown')
        )
        expected['extension'] = 'md'

    mocker.patch('webbrowser.open')
    mocker.patch('builtins.print')

    p = Path(tmpdir, uuid4().hex[:5])
    mocker.patch('builtins.input', side_effect=choice + [p.as_posix()])

    expected['output'] = 'save'

    ret = menu(Layout({'x': Integer(1)}))
    for k, v in expected.items():
        assert ret[k] == v
