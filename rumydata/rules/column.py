"""
column validation rules

These rules capture a common, but much more complex use case for data
validation, when it is necessary to compare the values of a single column across
multiple rows. The most intuitive example of this is the Unique rule, which
requires that every value in a column (excepting blanks) be unique/distinct.

These rules are intended to be used by adding them directly to rules argument in
the constructor of the classes in the field submodule.

Users of this package should be aware that the introduction of a column rule can
have a dramatic increase on the resources required to perform validation. If
there are no column validation rules present in a Layout, then each row will be
discarded from memory after validation is complete. However, each field that has
one or more column rules will require the entire to be available for validation.
In small data sets the impact will be minor, but larger data sets have the
potential to introduce performance impacts.
"""

from typing import List

from rumydata._base import _BaseRule

__all__ = ['Unique']


class Rule(_BaseRule):
    """ Column Rule """

    @staticmethod
    def _pre_process(data: List[str], **kwargs) -> List[str]:
        if kwargs.get('strip'):
            data = [d.strip() for d in data]
        return data

    def _prepare(self, data: List[str]) -> tuple:
        return data,


class Unique(Rule):
    """ Column values unique Rule """

    def _prepare(self, data: List[str]) -> tuple:
        return [x for x in data if not x == ''],

    def _evaluator(self):
        return lambda x: len(x) == len(set(x))

    def _exception_msg(self):
        return self.rule_exception()(self._explain())

    def _explain(self):
        return 'values must be unique'
