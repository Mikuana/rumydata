import tempfile
from pathlib import Path
from unittest.mock import DEFAULT
from uuid import uuid4

import pytest

from rumydata.field import Integer
from rumydata.menu import menu
from rumydata.table import Layout


def mock_no_md(*args, **kwargs):
    """ force exception on markdown module import """
    if args[0] == 'markdown':
        raise ModuleNotFoundError
    else:
        return DEFAULT


@pytest.fixture()
def tmpdir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


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
            'builtins.__import__', wraps=__import__, side_effect=mock_no_md
        )

    mocker.patch('webbrowser.open')
    mocker.patch('builtins.print')
    mocker.patch('builtins.input', return_value=choice)

    expected = dict(
        extension=ext, output='open', layout=Layout({'x': Integer(1)})
    )
    ret = menu(expected['layout'])
    for k, v in expected.items():
        assert ret[k] == v


@pytest.mark.parametrize('no_md', [False, True])
@pytest.mark.parametrize('choice,expected', [
    (['1', '0', '0'], dict(extension='md')),
    (['Generate Documentation', 'markdown', 'print'], dict(extension='md')),
    (['Generate Documentation', 'html', 'print'], dict(extension='html')),
])
def test_generate_documentation_print(choice, expected: dict, no_md, mocker):
    if no_md:
        mocker.patch(
            'builtins.__import__', wraps=__import__, side_effect=mock_no_md
        )
        expected['extension'] = 'md'

    mocker.patch('webbrowser.open')
    mocker.patch('builtins.print')
    mocker.patch('builtins.input', side_effect=choice)

    expected['output'] = 'print'
    expected['layout'] = Layout({'x': Integer(1)})

    ret = menu(expected['layout'])
    for k, v in expected.items():
        assert ret[k] == v


@pytest.mark.parametrize('no_md', [False, True])
@pytest.mark.parametrize('choice,expected', [
    (['1', '0', '1'], dict(extension='md')),
    (['Generate Documentation', 'markdown', 'save to file'], dict(extension='md')),
    (['Generate Documentation', 'html', 'save to file'], dict(extension='html')),
])
def test_generate_documentation_save(choice, expected: dict, no_md, tmpdir, mocker):
    if no_md:
        mocker.patch(
            'builtins.__import__', wraps=__import__, side_effect=mock_no_md
        )
        expected['extension'] = 'md'

    mocker.patch('webbrowser.open')
    mocker.patch('builtins.print')

    p = Path(tmpdir, uuid4().hex[:5])
    mocker.patch('builtins.input', side_effect=choice + [p.as_posix()])

    expected['output'] = 'save to file'
    expected['layout'] = Layout({'x': Integer(1)})

    ret = menu(expected['layout'])
    for k, v in expected.items():
        assert ret[k] == v
