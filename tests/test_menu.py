from unittest.mock import patch, DEFAULT

import pytest

from rumydata.field import Integer
from rumydata.menu import menu
from rumydata.table import Layout


@pytest.mark.parametrize('choice', ['0', 'View Documentation'])
def test_menu_view_documentation(choice):
    expected = dict(
        layout=Layout({'x': Integer(1)}),
        extension='html', output='open'
    )
    with patch('webbrowser.open'):  # don't open browser during testing
        with patch('builtins.print'):  # don't print during testing
            with patch('builtins.input', return_value=choice):
                ret = menu(expected['layout'])
                for k, v in expected.items():
                    assert ret[k] == v


@pytest.mark.parametrize('choice', ['0', 'View Documentation'])
def test_menu_view_documentation_no_html(choice):
    """
    When the markdown module is not available for HTML conversion, the output
    should be in raw markdown format.
    """

    def no_md(*args, **kwargs):
        if args[0] == 'markdown':
            raise ModuleNotFoundError
        else:
            return DEFAULT

    lay = Layout({'x': Integer(1)})
    expected = dict(extension='md', output='open', layout=lay)
    with patch('builtins.__import__', wraps=__import__, side_effect=no_md):
        with patch('webbrowser.open'):  # don't open browser during testing
            with patch('builtins.print'):  # don't print during testing
                with patch('builtins.input', return_value=choice):
                    ret = menu(lay)
                    for k, v in expected.items():
                        assert ret[k] == v

# @pytest.mark.parametrize('sequence', [
#     (['0']),
#     (['View Documentation'])
# ])
# def test_menu_generate_documentation(sequence):
#     lay = Layout({'x': Integer(1)})
#     expected = dict(extension='html', output='open', layout=lay)
#     with patch('webbrowser.open'):  # don't open browser during testing
#         with patch('builtins.print'):  # don't print during testing
#             with patch('builtins.input', side_effect=sequence):
#                 ret = menu(lay)
#                 for k, v in expected.items():
#                     assert ret[k] == v
