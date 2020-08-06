import csv
from pathlib import Path
from typing import Union

from rumydata import exception as ex
from rumydata.base import BaseSubject
from rumydata.field import Fields
from rumydata.rules import file, column as cr, header as hr, row as rr


class File(BaseSubject):
    def __init__(self, fields: Fields, max_errors=100, **kwargs):
        # pop any csv reader kwargs for later use
        x = {x: kwargs.pop(x, None) for x in ['dialect', 'delimiter', 'quotechar']}
        self.csv_kwargs = {k: v for k, v in x.items() if v}
        super().__init__(**kwargs)

        self.max_errors = max_errors
        self.fields = fields
        self.rules.extend([
            file.FileExists()
        ])

    def __check__(self, filepath: Union[str, Path], **kwargs):
        p = Path(filepath) if isinstance(filepath, str) else filepath
        e = super().__check__(p, rule_type=file.Rule)  # check files-based rules first
        if e:
            return ex.FileError(file=filepath, errors=e)

        column_cache = {
            k: [] for k, v in self.fields.definition.items()
            if v.has_rule_type(cr.Rule)
        }
        column_cache_map = {
            k: list(self.fields.definition.keys()).index(k)
            for k in column_cache.keys()
        }

        with open(p, newline='') as f:
            for rix, row in enumerate(csv.reader(f, **self.csv_kwargs)):
                rt = hr.Rule if rix == 0 else rr.Rule
                re = self.fields.__check__(row, rule_type=rt, rix=rix)
                if re:
                    e.append(re)
                    if rix == 0:  # if header error present, stop checking rows
                        break
                    if len(e) > self.max_errors:
                        m = f"max of {str(self.max_errors)} row errors exceeded"
                        e.append(ex.MaxExceededError(m))
                        break
                if rix > 0:
                    for k, ix in column_cache_map.items():
                        column_cache[k].append(row[ix])

        for k, v in column_cache.items():
            ce = self.fields.definition[k].__check__(v, rule_type=cr.Rule)
            if ce:
                e.append(ce)
        if e:
            return ex.FileError(file=p.name, errors=e)

    def check(self, file_path):
        errors = self.__check__(file_path)
        assert not errors, str(errors)
