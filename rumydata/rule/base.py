from rumydata import exception as ex


class BaseRule:
    """ Base class for defining data type rules """
    exception_class = ex.UrNotMyDataError

    def evaluator(self):
        """
        :return: a function which expects to evaluate to True if the value
        provided to the function meets the rule.
        """
        return lambda x: False  # default to failing evaluation if not overwritten

    def exception_msg(self):
        """
        :return: a sanitized error message which is specific to the function,
        contains no direct link to the value that was checked.
        """
        return self.exception_class(self.explain())

    def explain(self) -> str:
        """
        :return: an explanation of the rule that is applied
        """
        return "default rule explanation"


class CellRule(BaseRule):
    pass


class ColumnsRule(BaseRule):
    exception_class = ex.ColumnComparisonError

    def __init__(self, compare_to: str):
        self.compare_to = compare_to


class RowsRule(BaseRule):
    exception_class = ex.RowComparisonError


class MatrixRule(BaseRule):
    """ Will support comparison of different columns in different rows. Not yet implemented. """
    pass


class FileRule(BaseRule):
    pass


class HeaderRule(CellRule):
    def __init__(self, definition):
        self.definition = definition
