from typing import List, AnyStr

from rumydata import exception as ex
from rumydata.base import BaseRule


class Rule(BaseRule):
    def __init__(self, columns):
        self.definition = columns.definition

    def prepare(self, data: List[AnyStr]) -> tuple:
        return data,


class NoExtra(Rule):
    exception_class = ex.UnexpectedColumnError

    def evaluator(self):
        return lambda x: all([y in self.definition for y in x])

    def explain(self):
        return 'Header row must not have unexpected columns'


class NoMissing(Rule):
    exception_class = ex.MissingColumnError

    def evaluator(self):
        return lambda x: all([y in x for y in self.definition])

    def explain(self) -> str:
        return 'Header row must not be missing any expected columns'


class NoDuplicate(Rule):
    exception_class = ex.DuplicateColumnError

    def evaluator(self):
        return lambda x: len(x) == len(set(x))

    def explain(self):
        return 'Header row must not contain duplicate values'


class ColumnOrder(Rule):
    exception_class = ex.DataError

    def evaluator(self):
        return lambda x: x == list(self.definition)

    def explain(self):
        return 'Header row must explicitly match order of definition'
