"""
rumydata header rules

These rules are applied to header rows and are generally not intended to be
used directly. They ensure that the headers are named as expected, with no
missing names and no extras.
"""
from collections import namedtuple
from typing import List

from rumydata._base import _BaseRule

# a stand-in for a Layout (importing it here would be a circular import)
_default_thing = namedtuple('DefaultDict', ['layout', 'header_mode', 'empty_cols_ok'])


class Rule(_BaseRule):
    """ Header Rule """

    _default_args = (_default_thing({}, 'exact', False),)

    def __init__(self, columns):
        super().__init__()
        self.header_mode = columns.header_mode
        self.definition = columns.layout
        self.empty_cols_ok = columns.empty_cols_ok

    def _prepare(self, data: List[str]) -> tuple:
        if self.empty_cols_ok:
            return [x for x in data if x != ''],
        else:
            return data,


def _starts_with_ixs(x, keys):
    return [[y.startswith(z) for z in keys].index(True) for y in x]


def _contains_ixs(x, keys):
    return [[z in y for z in keys].index(True) for y in x]


def _is_unique(ixs):
    return len(ixs) == len(set(ixs))


def _is_sorted(ixs):
    return ixs == sorted(ixs)


class NoExtra(Rule):
    """ No extra header elements Rule """

    def _evaluator(self):
        modes = {
            'exact': lambda x: all([y in self.definition for y in x]),
            'startswith': lambda x: all([any([y.startswith(z) for z in self.definition]) for y in x]),
            'contains': lambda x: all([any([z in y for z in self.definition]) for y in x])
        }
        return modes[self.header_mode]

    def _explain(self):
        return 'Header row must not have unexpected columns'


class NoMissing(Rule):
    """ No missing header elements Rule """

    def _evaluator(self):
        modes = {
            'exact': lambda x: all([y in x for y in self.definition]),
            'startswith': lambda x: all([any([z.startswith(y) for z in x]) for y in self.definition]),
            'contains': lambda x: all([any([y in z for z in x]) for y in self.definition])
        }
        return modes[self.header_mode]

    def _explain(self) -> str:
        return 'Header row must not be missing any expected columns'


class NoDuplicate(Rule):
    """ No duplicate header elements Rule """

    def _evaluator(self):
        modes = {
            'exact': lambda x: len(x) == len(set(x)),
            'startswith': lambda x: _is_unique(_starts_with_ixs(x, self.definition.keys())),
            'contains': lambda x: _is_unique(_contains_ixs(x, self.definition.keys()))
        }
        return modes[self.header_mode]

    def _explain(self):
        return 'Header row must not contain duplicate values'


class ColumnOrder(Rule):
    """ Fixed header element order Rule """

    def _evaluator(self):
        modes = {
            'exact': lambda x: x == list(self.definition),
            'startswith': lambda x: _is_sorted(_starts_with_ixs(x, self.definition.keys())),
            'contains': lambda x: _is_sorted(_contains_ixs(x, self.definition.keys()))
        }
        return modes[self.header_mode]

    def _explain(self):
        return 'Header row must explicitly match order of definition'
