import csv
from pathlib import Path
from typing import Union

from rumydata import exception as ex
from rumydata.base import BaseSubject
from rumydata.file import rule
from rumydata.header import Header
from rumydata.row import Row


class File(BaseSubject):
    def __init__(self, layout, max_errors=100, **kwargs):
        # pop any csv reader kwargs for later use
        x = {x: kwargs.pop(x, None) for x in ['dialect', 'delimiter', 'quotechar']}
        self.csv_kwargs = {k: v for k, v in x.items() if v}
        super().__init__(**kwargs)

        self.max_errors = max_errors
        self.layout = layout
        self.rules.extend([
            rule.FileExists(),
            rule.FileNameMatchesPattern(self.layout.pattern),
        ])

    def __check__(self, filepath: Union[str, Path], **kwargs):
        p = Path(filepath) if isinstance(filepath, str) else filepath
        e = super().__check__(p)  # check file-based rules first
        if e:
            return ex.FileError(file=filepath, errors=e)

        with open(p) as f:
            hv, rv = Header(self.layout), Row(self.layout)
            for rix, row in enumerate(csv.reader(f, **self.csv_kwargs)):
                re = hv.__check__(row) if rix == 0 else rv.__check__(row, rix)
                if re:
                    e.append(re)
                    if rix == 0:  # if header error present, stop checking rows
                        break
                    if len(e) > self.max_errors:
                        m = f"max of {str(self.max_errors)} row errors exceeded"
                        e.append(ex.MaxExceededError(m))
                        break
        if e:
            return ex.FileError(file=p.name, errors=e)

    def check(self, file_path):
        errors = self.__check__(file_path)
        assert not errors, str(errors)
