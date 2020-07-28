from rumydata import exception as ex
from rumydata.base import BaseSubject
from rumydata.layout import Layout
from rumydata.header import rule


class Header(BaseSubject):
    def __init__(self, layout: Layout, **kwargs):
        super().__init__(**kwargs)

        self.rules.extend([
            rule.ColumnOrder(layout.definition),
            rule.NoExtra(layout.definition),
            rule.NoDuplicate(layout.definition),
            rule.NoMissing(layout.definition)
        ])

    def __check__(self, row: list, **kwargs):
        e = super().__check__(row)
        if e:  # if row errors are found, skip cell checks
            return ex.RowError(0, errors=e)

    def check(self, row):
        errors = self.__check__(row)
        assert not errors, str(errors)
