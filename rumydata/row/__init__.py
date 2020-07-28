from rumydata import exception as ex
from rumydata.base import BaseSubject
from rumydata.layout import Layout
from rumydata.row import rule


class Row(BaseSubject):
    def __init__(self, layout: Layout, **kwargs):
        super().__init__(**kwargs)
        self.definition = layout.definition

        self.rules.extend([
            rule.RowLengthLTE(len(self.definition)),
            rule.RowLengthGTE(len(self.definition))
        ])

    def __check__(self, row: list, rix=-1):
        e = super().__check__(row)
        if e:  # if row errors are found, skip cell checks
            return ex.RowError(rix, errors=e)

        row = dict(zip(self.definition.keys(), row))

        for cix, (name, val) in enumerate(row.items()):
            t = self.definition[name]
            comp = {k: row[k] for k in t.comparison_columns()}
            ce = t.__check__(val, cix, rix=rix, name=name, compare=comp)
            if ce:
                e.append(ce)
        if e:
            return ex.RowError(rix, errors=e)

    def check(self, row, **kwargs):
        errors = self.__check__(row, **kwargs)
        assert not errors, str(errors)
