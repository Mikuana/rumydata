"""
rumydata row rules

These rules are applied to entire rows and are generally not intended to be
used directly. They accomplish things like ensuring that the entire row contains
the expected number of values, before attempting to validate individual cells.
"""

from typing import List

from rumydata import field
from rumydata._base import _BaseRule


class Rule(_BaseRule):
    """ Row Rule """

    def __init__(self, layout):
        super().__init__()
        self.empty_cols_ok = layout.empty_cols_ok
        self.columns_length = layout.field_count
        self.definition = layout.layout

    def _prepare(self, data: List[str]) -> tuple:
        if self.empty_cols_ok:
            new_layout = self.definition.copy()
            for ix, x in enumerate(data):
                if not x:
                    new_layout[f'empty{str(ix)}'] = field.Text(0, nullable=True)
            if self.definition != new_layout:
                self.definition.update(new_layout)
                self.columns_length = len(self.definition)
                data = list(self.definition)
        return data,


class RowLengthLTE(Rule):
    """ Row length less than or equal to Rule """

    _default_args = (1,)

    def _evaluator(self):
        return lambda x: len(x) <= self.columns_length

    def _explain(self) -> str:
        return f'row length must be equal to {str(self.columns_length)}, not greater'


class RowLengthGTE(Rule):
    """ Row greater than or equal to Rule """

    _default_args = (1,)

    def _evaluator(self):
        return lambda x: len(x) >= self.columns_length

    def _explain(self) -> str:
        return f'row length must be equal to {str(self.columns_length)}, not less'
