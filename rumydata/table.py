"""
table submodule

This submodule contains the File class, and it's closely related Layout class.
"""

import csv
from pathlib import Path
from typing import Union, Dict, List

from rumydata import exception as ex
from rumydata import field
from rumydata._base import _BaseSubject
from rumydata.rules import table, column as cr, header as hr, row as rr, cell as clr


class Layout(_BaseSubject):
    """
    Table Layout Class

    This class contains a collection of Field objects which form a tabular data
    set. The initialized object is then used to check a row or header for
    validity.

    There are two main ways that this class is intended to be used:
        1. to generate technical documentation for the tabular data set
        2. to use in concert with a File object to validate the contents

    :param _definition: dictionary of column names with DataType definitions
    :param skip_header: (optional) a boolean control to skip validation of
        the header in the file. Defaults to False.
    :param empty_row_ok: (optional) a boolean control to skip validation of
        any row that is completely empty (i.e. every field is blank).
        Defaults to False.
    :param title: (optional) a brief name for the layout, which is included
        in the technical digest.
    """

    def __init__(self, _definition: Dict[str, field.Field], **kwargs):
        self.skip_header = kwargs.pop('skip_header', False)
        self.empty_row_ok = kwargs.pop('empty_row_ok', False)

        super().__init__(**kwargs)

        self.layout = _definition
        self.field_count = len(_definition)
        self._title = kwargs.get('title')

        self.rules.extend([
            hr.ColumnOrder(self),
            hr.NoExtra(self),
            hr.NoDuplicate(self),
            hr.NoMissing(self),
            rr.RowLengthLTE(self.field_count),
            rr.RowLengthGTE(self.field_count)
        ])

    def documentation(self):
        """
        Technical documentation

        Generates detailed specification of the defined layout.

        :return: a Markdown formatted string describing the layout
        """
        return self._markdown_digest()

    def check_header(self, row: List[str], rix=0):
        """
        Header Rule assertion

        Perform an assertion of the provided row against the header rules
        defined for this layout. If the row fails the check for any of the
        rules, the assertion will raise a detailed exception message.

        :param row: a list of strings which make up the header row
        :param rix: row index number. Used to report position of the header row
            in the file. Defaults to 0.
        """
        errors = self._check(row, rule_type=hr.Rule, rix=rix)
        assert not errors, str(errors)

    def check_row(self, row: List[str], rix=-1):
        """
        Row Rule assertion

        Perform an assertion of the provided row against the row rules
        defined for this layout. If the row fails the check for any of the
        rules, the assertion will raise a detailed exception message.

        :param row: a list of strings which make up the row
        :param rix: row index number. Used to report position of row in file.
        """
        errors = self._check(row, rule_type=rr.Rule, rix=rix)
        assert not errors, str(errors)

    def _markdown_digest(self) -> str:
        """
        Layout Markdown digest

        This method returns text in Markdown format, which provides a detailed
        technical specification for each field in the Layout.

        :return: a Markdown formatted string describing the layout
        """
        fields = f'# {self._title}' + '\n\n' if self._title else ''
        fields += '\n'.join([
            f' - **{k}**' + ''.join(['\n   - ' + x for x in v._digest()])
            for k, v in self.layout.items()
        ])
        return fields

    def _check(self, row, rule_type, rix=None) -> Union[ex.UrNotMyDataError, None]:
        if rule_type == hr.Rule and self.skip_header:
            return

        e = super()._check(row, rule_type=rule_type)

        if e:  # if row errors are found, skip cell checks
            return ex.RowError(rix or -1, errors=e)

        if rule_type == rr.Rule:
            row = dict(zip(self.layout.keys(), row))
            ignore = {k: isinstance(v, field.Ignore) for k, v in self.layout.items()}
            # if empty row is okay, and all fields are either empty, or Ignore class
            if self.empty_row_ok and all([('' if ignore[k] else v) == '' for k, v in row.items()]):
                return

            for cix, (name, val) in enumerate(row.items()):
                t = self.layout[name]
                comp = {k: row[k] for k in t._comparison_columns()}
                check_args = dict(
                    data=(val, comp), rule_type=clr.Rule,
                    rix=rix, cix=cix, name=name
                )
                ce = t._check(**check_args)
                if ce:
                    e.append(ce)
            if e:
                return ex.RowError(rix, errors=e)


class File(_BaseSubject):
    """
    File class

    This class provides a way to validate the contents of a file against a
    Layout, and report any rule violations that exist. This is the primary
    means of using this package.

    :param layout: a Layout object which defines the fields that make up the
        data set, along with the various rules that should be applied to
        each one.
    :param skip_rows: (optional) the number of rows to skip before starting
        evaluation. Defaults to 0.
    :param max_errors: (optional) the maximum number of row errors to be
        collected before halting validation of rows and raising a FileError.
        This is used to prevent overly verbose (and mostly useless)
        validation reports from being generated. Defaults to 100. The error
        limit can overwritten (set to unlimited) by providing a value of -1.
    :param file_type: (optional) the type of file to be evaluated. Valid
        values are ['csv', 'excel']. Defaults to 'csv'.
    :param dialect: (optional) only valid with csv file type. Controls csv
        dialect parsing.
    :param delimiter: (optional) only valid with csv file type. Controls csv
        delimiter parsing.
    :param quotechar: (optional) only valid with csv file type. Controls csv
        quote character parsing.
    :param sheet: (optional) only valid with excel file type. Determines
        which sheet will be read for tabular data evaluation.
    """

    def __init__(self, layout: Union[Layout, Dict], **kwargs):
        self.max_errors = kwargs.pop('max_errors', 100)
        self.file_type = kwargs.pop('file_type', 'csv')

        if self.file_type == 'csv':
            x = {x: kwargs.pop(x, None) for x in ['dialect', 'delimiter', 'quotechar']}
            self.csv_kwargs = {k: v for k, v in x.items() if v}
        elif self.file_type == 'excel':
            x = {x: kwargs.pop(x, None) for x in ['sheet']}
            self.excel_kwargs = {k: v for k, v in x.items() if v}
        else:
            raise TypeError(f'Invalid file type: {self.file_type}')

        self.skip_rows = kwargs.pop('skip_rows', 0)

        super().__init__(**kwargs)

        self.layout = Layout(layout) if isinstance(layout, Dict) else layout
        self.rules.extend([
            table.FileExists()
        ])

    def check(self, file_path: Union[str, Path]) -> None:
        """
        File check method

        Perform a check of the layout in this object against a file.

        :param file_path: a file path provided as a string, or a pathlib Path
            object.
        """
        errors = self._check(file_path)
        assert not errors, str(errors)

    def _check(self, filepath: Union[str, Path], **kwargs) -> Union[ex.FileError, None]:
        p = Path(filepath) if isinstance(filepath, str) else filepath
        e = super()._check(p, rule_type=table.Rule)  # check files-based rules first
        if e:
            return ex.FileError(file=filepath, errors=e)

        column_cache = {
            k: [] for k, v in self.layout.layout.items()
            if v._has_rule_type(cr.Rule)
        }
        column_cache_map = {
            k: list(self.layout.layout.keys()).index(k)
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

            max_error_rule = table.MaxError(self.max_errors)
            for rix, row in enumerate(generator):
                if rix < self.skip_rows:
                    continue
                row = row_handler(row)
                rt = hr.Rule if rix == (0 + self.skip_rows) else rr.Rule
                re = self.layout._check(row, rule_type=rt, rix=rix)
                if re:
                    e.append(re)
                    if rix == 0:  # if header error present, stop checking rows
                        break
                    if len(e) > self.max_errors:
                        e.append(max_error_rule._exception_msg())
                        break
                if rix > 0:
                    for k, ix in column_cache_map.items():
                        column_cache[k].append(row[ix])

        for k, v in column_cache.items():
            ce = self.layout.layout[k]._check(
                v, cix=column_cache_map[k], rule_type=cr.Rule, name=k
            )
            if ce:
                e.append(ce)
        if e:
            return ex.FileError(file=p.name, errors=e)
