from rumydata import exception as ex
from rumydata.base import BaseRule


class Rule(BaseRule):
    exception_class = ex.RowComparisonError


class RowLengthLTE(Rule):
    exception_class = ex.RowLengthError

    def __init__(self, comparison_value):
        self.comparison_value = comparison_value

    def evaluator(self):
        return lambda x: len(x) <= self.comparison_value

    def explain(self) -> str:
        return f'row length must be equal to {str(self.comparison_value)}, not greater'


class RowLengthGTE(Rule):
    exception_class = ex.RowLengthError

    def __init__(self, comparison_value):
        self.comparison_value = comparison_value

    def evaluator(self):
        return lambda x: len(x) >= self.comparison_value

    def explain(self) -> str:
        return f'row length must be equal to {str(self.comparison_value)}, not less'
