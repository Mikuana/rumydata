import rumydata.base
from rumydata import exception as ex
from rumydata.base import BaseSubject, CellData, RowData
from rumydata.row import rule


class Row(BaseSubject):
    def __init__(self, columns: rumydata.base.Columns, **kwargs):
        super().__init__(**kwargs)
        self.columns = columns

        self.rules.extend([
            rule.RowLengthLTE(self.columns.length),
            rule.RowLengthGTE(self.columns.length)
        ])

    def __check__(self, row: RowData, rix=-1, rule_type=rule.Rule):
        e = super().__check__(row, rule_type=rule_type)
        if e:  # if row errors are found, skip cell checks
            return ex.RowError(rix, errors=e)

        row = dict(zip(self.columns.definition.keys(), row.values))

        for cix, (name, val) in enumerate(row.items()):
            t = self.columns.definition[name]
            comp = {k: row[k] for k in t.comparison_columns()}
            ce = t.__check__(CellData(val, comp), cix, rix=rix, name=name)
            if ce:
                e.append(ce)
        if e:
            return ex.RowError(rix, errors=e)

    def check(self, row, **kwargs):
        errors = self.__check__(row, **kwargs)
        assert not errors, str(errors)
