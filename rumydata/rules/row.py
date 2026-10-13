"""
row validation rules

These rules are applied to entire rows and are generally not intended to be
used directly. They accomplish things like ensuring that the entire row contains
the expected number of values, before attempting to validate individual cells.
"""
from operator import ge, le
from typing import List

from rumydata._base import _BaseRule


class Rule(_BaseRule):
    """ Row Rule """

    def _prepare(self, data: List[str]) -> tuple:
        return data,


class _LengthComparison:
    """ Shared row length comparison mechanism

    Not a Rule subclass itself: the length rules combine it with Rule, so it
    adds no node to the Rule subclass tree that the generic rule tests walk.
    """

    comparison_op = None
    _direction = 'N/A'
    _default_args = (1,)

    def __init__(self, columns_length):
        super().__init__()
        self.columns_length = columns_length

    def _evaluator(self):
        # the base is abstract; concrete length rules set comparison_op
        if self.comparison_op is None:
            return lambda x: False
        op = self.comparison_op
        return lambda x: op(len(x), self.columns_length)

    def _explain(self) -> str:
        return f'row length must be equal to {str(self.columns_length)}, not {self._direction}'


class RowLengthLTE(_LengthComparison, Rule):
    """ Row length less than or equal to Rule """

    comparison_op = le
    _direction = 'greater'


class RowLengthGTE(_LengthComparison, Rule):
    """ Row length greater than or equal to Rule """

    comparison_op = ge
    _direction = 'less'
