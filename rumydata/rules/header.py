"""
rumydata row rules

These rules are applied to header rows and are generally not intended to be
used directly. These rules ensure that the headers are named as expected, is
not missing any names, or containing any extras.
"""

from typing import List

from rumydata import exception as ex
from rumydata.base import BaseRule


class Rule(BaseRule):
    """ Header Rule """

    def __init__(self, columns):
        self.definition = columns.definition

    def _prepare(self, data: List[str]) -> tuple:
        return data,


class NoExtra(Rule):
    """ No extra header elements Rule """

    exception_class = ex.UnexpectedColumnError

    def _evaluator(self):
        return lambda x: all([y in self.definition for y in x])

    def _explain(self):
        return 'Header row must not have unexpected columns'


class NoMissing(Rule):
    """ No missing header elements Rule """

    exception_class = ex.MissingColumnError

    def _evaluator(self):
        return lambda x: all([y in x for y in self.definition])

    def _explain(self) -> str:
        return 'Header row must not be missing any expected columns'


class NoDuplicate(Rule):
    """ No duplicate header elements Rule """
    exception_class = ex.DuplicateColumnError

    def _evaluator(self):
        return lambda x: len(x) == len(set(x))

    def _explain(self):
        return 'Header row must not contain duplicate values'


class ColumnOrder(Rule):
    """ Fixed header element order Rule """

    exception_class = ex.DataError

    def _evaluator(self):
        return lambda x: x == list(self.definition)

    def _explain(self):
        return 'Header row must explicitly match order of definition'
