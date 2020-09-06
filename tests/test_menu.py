import pytest
from unittest.mock import patch

from rumydata.menu import menu
from rumydata.table import Layout
from rumydata.field import Integer


@pytest.mark.parametrize('sequence,outcome', [
    (['0'], 'completed'),
    (['1'], 'completed')
])
def test_menu_open_browser(sequence, outcome):
    lay = Layout({'x': Integer(1)})
    with patch('webbrowser.open'):  # don't open browser during testing
        with patch('builtins.input', side_effect=sequence):
            assert menu(lay)
