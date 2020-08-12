import csv
from pathlib import Path
from typing import Union, Dict

from rumydata import exception as ex
from rumydata import field
from rumydata.base import BaseSubject
from rumydata.rules import file, column as cr, header as hr, row as rr, cell as clr


class Layout(BaseSubject):
    def __init__(self, definition: dict, **kwargs):
        """
        Defines the layout of a tabular files.

        :param definition: dictionary of column names with DataType definitions
        """
        self.skip_header = kwargs.pop('skip_header', False)
        self.empty_row_ok = kwargs.pop('empty_row_ok', False)

        super().__init__(**kwargs)

        self.definition = definition
        self.length = len(definition)
        self.title = kwargs.get('title')

        self.rules.extend([
            hr.ColumnOrder(self),
            hr.NoExtra(self),
            hr.NoDuplicate(self),
            hr.NoMissing(self),
            rr.RowLengthLTE(self.length),
            rr.RowLengthGTE(self.length)
        ])

    def __check__(self, row, rule_type, rix=None):
        if rule_type == hr.Rule and self.skip_header:
            return

        e = super().__check__(row, rule_type=rule_type)

        if e:  # if row errors are found, skip cell checks
            return ex.RowError(rix or -1, errors=e)

        if rule_type == rr.Rule:
            row = dict(zip(self.definition.keys(), row))
            ignore = {k: isinstance(v, field.Ignore) for k, v in self.definition.items()}
            # if empty row is okay, and all fields are either empty, or Ignore class
            if self.empty_row_ok and all([('' if ignore[k] else v) == '' for k, v in row.items()]):
                return

            for cix, (name, val) in enumerate(row.items()):
                t = self.definition[name]
                comp = {k: row[k] for k in t.comparison_columns()}
                check_args = dict(
                    data=(val, comp), rule_type=clr.Rule,
                    rix=rix, cix=cix, name=name
                )
                ce = t.__check__(**check_args)
                if ce:
                    e.append(ce)
            if e:
                return ex.RowError(rix, errors=e)

    def check_header(self, row, rix=0):
        errors = self.__check__(row, rule_type=hr.Rule, rix=rix)
        assert not errors, str(errors)

    def check_row(self, row, rix=-1):
        errors = self.__check__(row, rule_type=rr.Rule, rix=rix)
        assert not errors, str(errors)

    def digest(self):
        return [[f'Name: {k}', *v.digest()] for k, v in self.definition.items()]

    def markdown_digest(self):
        fields = f'# {self.title}' + '\n\n' if self.title else ''
        fields += '\n'.join([
            f' - **{k}**' + ''.join(['\n   - ' + x for x in v.digest()])
            for k, v in self.definition.items()
        ])
        return fields

    def comparison_columns(self):
        compares = set()
        for v in self.definition.values():
            compares.update(v.comparison_columns())
        return compares


class File(BaseSubject):
    def __init__(self, layout: Union[Layout, Dict], max_errors=100, **kwargs):
        self.file_type = kwargs.pop('file_type', 'csv')

        if self.file_type == 'csv':
            x = {x: kwargs.pop(x, None) for x in ['dialect', 'delimiter', 'quotechar']}
            self.csv_kwargs = {k: v for k, v in x.items() if v}
        elif self.file_type == 'excel':
            x = {x: kwargs.pop(x, None) for x in ['sheet']}
            self.excel_kwargs = {k: v for k, v in x.items() if v}
        else:
            raise Exception(f'Invalid file type: {self.file_type}')

        self.skip_rows = kwargs.pop('skip_rows', 0)

        super().__init__(**kwargs)

        self.max_errors = max_errors
        self.layout = Layout(layout) if isinstance(layout, Dict) else layout
        self.rules.extend([
            file.FileExists()
        ])

    def __check__(self, filepath: Union[str, Path], **kwargs):
        p = Path(filepath) if isinstance(filepath, str) else filepath
        e = super().__check__(p, rule_type=file.Rule)  # check files-based rules first
        if e:
            return ex.FileError(file=filepath, errors=e)

        column_cache = {
            k: [] for k, v in self.layout.definition.items()
            if v.has_rule_type(cr.Rule)
        }
        column_cache_map = {
            k: list(self.layout.definition.keys()).index(k)
            for k in column_cache.keys()
        }

        with open(p, newline='') as f:
            if self.file_type == 'csv':
                generator = csv.reader(f, **self.csv_kwargs)

                def row_handler(r):  # handle csv rows as-is
                    return r
            elif self.file_type == 'excel':
                from openpyxl import load_workbook
                wb = load_workbook(p)
                sheet = self.excel_kwargs.get('sheet')
                ws = wb.get_sheet_by_name(sheet) if sheet else wb.active
                generator = ws.values

                def row_handler(r):  # convert values to strings and replace None with empty
                    return [str(x or '') for x in r]

            for rix, row in enumerate(generator):
                if rix < self.skip_rows:
                    continue
                row = row_handler(row)
                rt = hr.Rule if rix == (0 + self.skip_rows) else rr.Rule
                re = self.layout.__check__(row, rule_type=rt, rix=rix)
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
            ce = self.layout.definition[k].__check__(v, rule_type=cr.Rule)
            if ce:
                e.append(ce)
        if e:
            return ex.FileError(file=p.name, errors=e)

    def check(self, file_path):
        errors = self.__check__(file_path)
        assert not errors, str(errors)
