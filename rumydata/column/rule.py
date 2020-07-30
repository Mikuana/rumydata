from rumydata import exception as ex
from rumydata.base import BaseRule, CellData


class Rule(BaseRule):
    exception_class = ex.ColumnComparisonError

    def __init__(self, compare_to: str):
        self.compare_to = compare_to

    def prepare(self, data: CellData) -> tuple:
        return data.value, data.compare[self.compare_to]


class GreaterThanColumn(Rule):
    def evaluator(self):
        return lambda x, y: x > y

    def explain(self) -> str:
        return f"must be greater than column '{self.compare_to}'"
