from rumydata import exception as ex
from rumydata.base import BaseRule, ColumnData


class Rule(BaseRule):

    def prepare(self, data: ColumnData) -> tuple:
        return data.values,


class Unique(Rule):
    exception_class = ex.DataError

    def prepare(self, data: ColumnData) -> tuple:
        return [x for x in ColumnData.values if not x == ''],

    def evaluator(self):
        return lambda x: len(x) == len(set(x))

    def exception_msg(self):
        return self.exception_class(self.explain())

    def explain(self):
        return 'values must be unique'
