"""
rumydata row rules

These rules are applied to header rows and are generally not intended to be
used directly. These rules ensure that the headers are named as expected, is
not missing any names, or containing any extras.
"""
from collections import namedtuple
from typing import List

from rumydata._base import _BaseRule

# this named tuple is here to allow for setting the default argument without
# needing to import the Layout class, which results in a circular import
_default_thing = namedtuple('DefaultDict', ['layout'])


class Rule(_BaseRule):
    """ Header Rule """

    _default_args = (_default_thing({}),)

    def __init__(self, columns):
        super().__init__()
        self.definition = columns.layout

    def _prepare(self, data: List[str]) -> tuple:
        return data,


class NoExtra(Rule):
    """ No extra header elements Rule """

    def _evaluator(self):
        return lambda x: all([y in self.definition for y in x])

    def _explain(self):
        return 'Header row must not have unexpected columns'


class NoMissing(Rule):
    """ No missing header elements Rule """

    def _evaluator(self):
        return lambda x: all([y in x for y in self.definition])

    def _explain(self) -> str:
        return 'Header row must not be missing any expected columns'


class NoDuplicate(Rule):
    """ No duplicate header elements Rule """

    def _evaluator(self):
        return lambda x: len(x) == len(set(x))

    def _explain(self):
        return 'Header row must not contain duplicate values'


class ColumnOrder(Rule):
    """ Fixed header element order Rule """

    def _evaluator(self):
        return lambda x: x == list(self.definition)

    def _explain(self):
        return 'Header row must explicitly match order of definition'
