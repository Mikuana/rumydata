import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

from rumydata.field import Integer, Field
from rumydata.rules.column import Unique
from rumydata.table import Layout, File


@pytest.fixture()
def tmpdir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


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
        File(lay).check(p)
    except AssertionError as ae:
        print(ae)
        print(msg)
        assert str(ae).endswith(msg)


def test_documentation():
    """ An equally silly test of documentation output """
    layout = Layout({'x': Field()})
    expected = ' - **x**\n   - cannot be empty/blank'
    assert layout.documentation() == expected
