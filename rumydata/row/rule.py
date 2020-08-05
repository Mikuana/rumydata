from rumydata import exception as ex
from rumydata.base import BaseRule, RowData


class Rule(BaseRule):
    exception_class = ex.RowComparisonError

    def prepare(self, data: RowData) -> tuple:
        return data.values,


class RowLengthLTE(Rule):
    exception_class = ex.RowLengthError

    def __init__(self, columns_length):
        self.columns_length = columns_length

    def evaluator(self):
        return lambda x: len(x) <= self.columns_length

    def explain(self) -> str:
        return f'row length must be equal to {str(self.columns_length)}, not greater'


class RowLengthGTE(Rule):
    exception_class = ex.RowLengthError

    def __init__(self, columns_length):
        self.columns_length = columns_length

    def evaluator(self):
        return lambda x: len(x) >= self.columns_length

    def explain(self) -> str:
        return f'row length must be equal to {str(self.columns_length)}, not less'
