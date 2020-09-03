"""
rumydata row rules

These rules are applied to entire rows and are generally not intended to be
used directly. They accomplish things like ensuring that the entire row contains
the expected number of values, before attempting to validate individual cells.
"""

from typing import List

from rumydata._base import _BaseRule


class Rule(_BaseRule):
    """ Row Rule """

    def _prepare(self, data: List[str]) -> tuple:
        return data,


class RowLengthLTE(Rule):
    """ Row length less than or equal to Rule """

    _default_args = (1,)

    def __init__(self, columns_length):
        super().__init__()
        self.columns_length = columns_length

    def _evaluator(self):
        return lambda x: len(x) <= self.columns_length

    def _explain(self) -> str:
        return f'row length must be equal to {str(self.columns_length)}, not greater'


class RowLengthGTE(Rule):
    """ Row greater than or equal to Rule """

    _default_args = (1,)

    def __init__(self, columns_length):
        super().__init__()
        self.columns_length = columns_length

    def _evaluator(self):
        return lambda x: len(x) >= self.columns_length

    def _explain(self) -> str:
        return f'row length must be equal to {str(self.columns_length)}, not less'
