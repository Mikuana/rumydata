import csv
from pathlib import Path
from typing import Union

from rumydata import column
from rumydata import exception as ex
from rumydata.base import BaseSubject, Columns, RowData
from rumydata.file import rule
from rumydata.header import Header
from rumydata.row import Row


class File(BaseSubject):
    def __init__(self, columns: Columns, max_errors=100, **kwargs):
        # pop any csv reader kwargs for later use
        x = {x: kwargs.pop(x, None) for x in ['dialect', 'delimiter', 'quotechar']}
        self.csv_kwargs = {k: v for k, v in x.items() if v}
        super().__init__(**kwargs)

        self.max_errors = max_errors
        self.columns = columns
        self.rules.extend([
            rule.FileExists()
        ])

    def __check__(self, filepath: Union[str, Path], **kwargs):
        p = Path(filepath) if isinstance(filepath, str) else filepath
        e = super().__check__(p, restrict=rule.Rule)  # check file-based rules first
        if e:
            return ex.FileError(file=filepath, errors=e)

        column_cache = {
            k: [] for k, v in self.columns.definition.items()
            if v.has_rule_type(column.rule.Rule)
        }
        column_cache_map = {
            k: list(self.columns.definition.keys()).index(k)
            for k in column_cache.keys()
        }

        with open(p) as f:
            hv, rv = Header(self.columns), Row(self.columns)
            for rix, row in enumerate(csv.reader(f, **self.csv_kwargs)):
                row = RowData(row)
                re = hv.__check__(row) if rix == 0 else rv.__check__(row, rix)
                if re:
                    e.append(re)
                    if rix == 0:  # if header error present, stop checking rows
                        break
                    if len(e) > self.max_errors:
                        m = f"max of {str(self.max_errors)} row errors exceeded"
                        e.append(ex.MaxExceededError(m))
                        break
                for k, ix in column_cache_map.items():
                    column_cache[k].append(row.values[ix])

        # for k, v in column_cache.items():
        #     ce = self.columns.definition[k].__check__(
        #         ColumnData(v), restrict=column.rule.Rule
        #     )
        #     if ce:
        #         e.append(ce)
        if e:
            return ex.FileError(file=p.name, errors=e)

    def check(self, file_path):
        errors = self.__check__(file_path)
        assert not errors, str(errors)
