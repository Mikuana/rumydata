from rumydata import exception as ex
from rumydata.rule.base import CellRule, ColumnsRule, RowsRule, HeaderRule, FileRule

__all__ = [
    'CellRule', 'ColumnsRule', 'RowsRule', 'HeaderRule', 'FileRule',
    'make_static_cell_rule'
]


def make_static_cell_rule(func, assertion, exception=ex.UrNotMyDataError) -> CellRule:
    """
    Return a factory generated Rule class. The function used by the rule must
    directly evaluate a single positional argument (i.e. x, but not x and y).
    Because the Rule cannot be passed a value on initialization, neither the
    evaluator or explain methods in the return class can be dynamic.
    """

    class FactoryRule(CellRule):
        exception_class = exception

        @classmethod
        def evaluator(cls):
            return func

        @classmethod
        def explain(cls) -> str:
            return assertion

    return FactoryRule()
