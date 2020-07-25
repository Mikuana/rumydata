from rumydata import exception as ex
from rumydata.rule.base import HeaderRule


class HeaderNoExtra(HeaderRule):
    exception_class = ex.UnexpectedColumnError

    def evaluator(self):
        return lambda x: all([y in self.definition for y in x])

    def explain(self):
        return 'Header row must not have unexpected columns'


class HeaderNoMissing(HeaderRule):
    exception_class = ex.MissingColumnError

    def evaluator(self):
        return lambda x: all([y in x for y in self.definition])

    def explain(self) -> str:
        return 'Header row must not be missing any expected columns'


class HeaderNoDuplicate(HeaderRule):
    exception_class = ex.DuplicateColumnError

    def evaluator(self):
        return lambda x: len(x) == len(set(x))

    def explain(self):
        return 'Header row must not contain duplicate values'


class HeaderColumnOrder(HeaderRule):
    exception_class = ex.DataError

    def evaluator(self):
        return lambda x: x == list(self.definition)

    def explain(self):
        return 'Header row must explicitly match order of definition'
