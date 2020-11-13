"""
rumydata row rules

These rules are applied to entire rows and are generally not intended to be
used directly. They accomplish things like ensuring that the entire row contains
the expected number of values, before attempting to validate individual cells.
"""

from typing import List
from collections import namedtuple

from rumydata import field
from rumydata._base import _BaseRule

# this named tuple is here to allow for setting the default argument without
# needing to import the Layout class, which results in a circular import
_default_thing = namedtuple('DefaultDict', ['lay', 'empty_cols_ok', 'field_count', 'layout'])


class Rule(_BaseRule):
    """ Row Rule """

    def __init__(self):
        super().__init__()

    def _prepare(self, data: List[str]) -> tuple:
        return data,


class RowLength(Rule):
    """ Generic Row length Rule """
    _default_args = (_default_thing({}, False, 1, {}),)

    def __init__(self, layout):
        super().__init__()
        self.empty_cols_ok = layout.empty_cols_ok
        self.columns_length = layout.field_count
        self.definition = layout.layout

    def _prepare(self, data: List[str]) -> tuple:
        if self.empty_cols_ok:
            if self.columns_length != len(data):
                self.columns_length = len(data)
        return data,


class RowLengthLTE(RowLength):
    """ Row length less than or equal to Rule """

    def _evaluator(self):
        return lambda x: len(x) <= self.columns_length

    def _explain(self) -> str:
        return f'row length must be equal to {str(self.columns_length)}, not greater'


class RowLengthGTE(RowLength):
    """ Row greater than or equal to Rule """

    def _evaluator(self):
        return lambda x: len(x) >= self.columns_length

    def _explain(self) -> str:
        return f'row length must be equal to {str(self.columns_length)}, not less'
