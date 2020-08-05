from rumydata import exception as ex
from rumydata.base import BaseSubject, Columns, RowData
from rumydata.header import rule


class Header(BaseSubject):
    def __init__(self, columns: Columns, **kwargs):
        super().__init__(**kwargs)

        self.rules.extend([
            rule.ColumnOrder(columns),
            rule.NoExtra(columns),
            rule.NoDuplicate(columns),
            rule.NoMissing(columns)
        ])

    def __check__(self, row: RowData, **kwargs):
        e = super().__check__(row, restrict=rule.Rule)
        if e:  # if row errors are found, skip cell checks
            return ex.RowError(0, errors=e)

    def check(self, row):
        errors = self.__check__(row)
        assert not errors, str(errors)
