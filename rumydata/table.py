"""
table submodule

This submodule contains the File class, and it's closely related Layout class.
"""
import csv
from pathlib import Path
from typing import Union, Dict, List, Iterable
from uuid import uuid4

from rumydata import exception as ex
from rumydata import field
from rumydata._base import _BaseSubject
from rumydata.rules import table, column as cr, header as hr, row as rr, cell as clr

__all__ = ['Layout', 'CsvFile', 'ExcelFile', 'ParquetFile']


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
    :param no_header: (optional) a boolean control that indicates that there is
        no header in the layout, and that every row should be treated as data.
        Defaults to False.
    :param header_mode: (optional) sets the mode for checking the header.
        Defaults to 'exact', but also accepts 'startswith' and 'contains'. This
        allows optional partial matching of header values in a layout to the
        values obtained in tabular data.
    :param empty_row_ok: (optional) a boolean control to skip validation of
        any row that is completely empty (i.e. every field is blank).
        Defaults to False.
    :param title: (optional) a brief name for the layout, which is included
        in the technical digest.
    :param use_excel_cell_format: (optional) a boolean control to specify whether to use Excel-style cell naming
    (e.g. A1 to represent rix=1, cix=1, AA20 to represent rix=20, cix=27, etc.) when reporting validation errors.
    """

    def __init__(self, _definition: Dict[str, field.Field], **kwargs):
        self.skip_header = kwargs.pop('skip_header', False)
        self.empty_row_ok = kwargs.pop('empty_row_ok', False)
        self.header_mode = kwargs.pop('header_mode', 'exact')
        self.empty_cols_ok = kwargs.pop('empty_cols_ok', False)
        self.use_excel_cell_format = kwargs.pop('use_excel_cell_format', False)
        self.no_header = kwargs.pop('no_header', False)
        header_modes = ('exact', 'startswith', 'contains')
        if self.header_mode not in header_modes:
            raise ValueError(f"header_mode argument invalid. Must be one of: {header_modes}")

        super().__init__(**kwargs)

        self.layout = _definition
        self._title = kwargs.get('title')

        self.rules.extend([
            hr.ColumnOrder(self),
            hr.NoExtra(self),
            hr.NoDuplicate(self),
            hr.NoMissing(self),
            rr.RowLengthLTE(self.field_count()),
            rr.RowLengthGTE(self.field_count())
        ])

    def field_count(self):
        return len(self.layout)

    def documentation(self, doc_type='md'):
        """
        Technical documentation

        Generates detailed specification of the defined layout.

        :param doc_type: format of returned technical documentation

        :return: a Markdown formatted string describing the layout
        """
        if doc_type == 'md':
            return self._markdown_digest()
        elif doc_type == 'html':
            import markdown
            return markdown.markdown(self._markdown_digest(), tab_length=2)
        else:
            raise TypeError(f"Invalid format type: {doc_type}")

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
            # if any of the fields are Ignore, or if the field uses the _ignore_if parameter and the value matches the
            # specified value we ignore them. Handles cases where a string or list is specified
            ignore = {k: (isinstance(v, field.Ignore) if isinstance(v, field.Ignore) else row[k] in self.layout[
                k]._ignore_if if isinstance(self.layout[k]._ignore_if, List) else row[k] == self.layout[k]._ignore_if)
                      for k, v in self.layout.items()}

            # if empty row is okay, and all fields are either empty, or Ignore class
            if self.empty_row_ok and all([('' if ignore[k] else v) == '' for k, v in row.items()]):
                return

            for cix, (name, val) in enumerate(row.items()):
                t = self.layout[name]
                comp = {k: row[k] for k in t._comparison_columns()}
                check_args = dict(
                    data=(val, comp), rule_type=clr.Rule,
                    rix=rix, cix=cix, name=name, use_excel_cell_format=self.use_excel_cell_format
                )
                ce = t._check(**check_args)
                if ce:
                    e.append(ce)
            if e:
                return ex.RowError(rix, errors=e)


class _BaseFile(_BaseSubject):
    """
    Base File class

    This class provides a way to validate the contents of a file against a
    Layout, and report any rule violations that exist. This is the primary
    means of using this package.

    :param layout: a Layout object which defines the fields that make up the
        data set, along with the various rules that should be applied to
        each one.
    :param skip_rows: the number of rows to skip before starting evaluation.
    :param max_errors: the maximum number of row errors to be
        collected before halting validation of rows and raising a FileError.
        This is used to prevent overly verbose (and mostly useless)
        validation reports from being generated. The error limit can be set to
        unlimited by providing a value of -1.
    :param ignore_exceptions: (optional) specify a dictionary of column names
        mapping to a value or list of values which will force the field to be
        treated as an Ignore field when the value is encountered.
    """

    def __init__(self, layout: Layout, skip_rows=0, max_errors=100, file_name_pattern=False, **kwargs):
        self.skip_rows = skip_rows
        self.max_errors = max_errors
        self.ignore_exceptions = kwargs.pop('ignore_exceptions', None)

        super().__init__(**kwargs)
        self.layout = Layout(layout) if isinstance(layout, Dict) else layout

        if self.ignore_exceptions:
            for k, v in self.ignore_exceptions.items():
                self.layout.layout[k]._ignore_if = v

        self.rules.extend([
            table.FileExists()
        ])
        if file_name_pattern:
            self.rules.append(table.FileNameMatch(file_name_pattern))

    def check(self, file_path: Union[str, Path], doc_type: str = None):
        """
        File check method

        Perform a check of the layout in this object against a file.

        :param file_path: a file path provided as a string, or a pathlib Path
            object.
        :param doc_type: the type of output to return with exception details,
            rather than raising an exception. Valid options are ['md', 'html']
        """
        errors = self._check(Path(file_path))
        try:
            assert not errors, str(errors)
            msg = f"Validated file successfully: {Path(file_path).as_posix()}"
        except AssertionError as ae:
            if not doc_type:
                raise ae
            else:
                msg = str(ae)

        if not doc_type:
            return
        elif doc_type == 'md':
            return msg
        elif doc_type == 'html':
            import markdown
            return markdown.markdown(msg, tab_length=2)
        else:
            raise TypeError(f"Invalid doc type: {doc_type}")

    def _rows(self, file: Path):
        pass

    @staticmethod
    def _row_handler(row: list) -> List[str]:
        return row

    def _check(self, filepath: Union[str, Path], **kwargs) -> Union[ex.FileError, None]:
        p = Path(filepath) if isinstance(filepath, str) else filepath
        e = super()._check(p, rule_type=table.Rule)  # check files-based rules first
        if e:
            return ex.FileError(file=p.name, errors=e)

        column_cache = {
            k: [] for k, v in self.layout.layout.items()
            if v._has_rule_type(cr.Rule)
        }
        column_cache_map = {
            k: list(self.layout.layout.keys()).index(k)
            for k in column_cache.keys()
        }

        max_error_rule = table.MaxError(self.max_errors)
        with self._rows(p) as generator:
            for rix, row in enumerate(generator):
                if rix < self.skip_rows:
                    continue
                row = self._row_handler(row)
                if rix == (0 + self.skip_rows) and self.layout.no_header is False:  # if header
                    re = self.layout._check(row, rule_type=hr.Rule, rix=rix)
                    if self.layout.empty_cols_ok:
                        # remap layout positions with Empty columns wherever header is empty
                        empties = [ix for ix, i in enumerate(row) if i == '']
                        bumps = {k: ix for ix, k in enumerate(self.layout.layout.keys())}

                        for i in empties:
                            for k, v in bumps.items():
                                if v >= i:
                                    bumps[k] += 1

                        bumps = {v: k for k, v in bumps.items()}
                        bumps = [bumps.get(i, f"empty_{uuid4().hex[:5]}") for i in range(len(row))]
                        # strip out the "trailing" empty columns before updating the field_count for the row length
                        # rules. These might get picked up when processing excel file layouts based on how the
                        # worksheet is configured, which would result in a mismatch between the number of columns
                        # rumydata sees in the row data and the number of columns which get inferred by reading the
                        # worksheet
                        while bumps[-1].startswith('empty_'):
                            bumps.pop()
                        self.layout.layout = {k: self.layout.layout.get(k, field.Empty()) for k in bumps}

                        for ix, rule in enumerate(self.layout.rules):  # update row length rules
                            if isinstance(rule, (rr.RowLengthLTE, rr.RowLengthGTE)):
                                self.layout.rules[ix].columns_length = self.layout.field_count()

                elif self.layout.empty_cols_ok:
                    cleaned_col_count = self.layout.field_count()
                    row = row[:cleaned_col_count]
                    re = self.layout._check(row, rule_type=rr.Rule, rix=rix)
                else:
                    re = self.layout._check(row, rule_type=rr.Rule, rix=rix)

                if re:
                    e.append(re)
                    if rix == (
                            0 + self.skip_rows) and self.layout.no_header is False:  # if header error present, stop checking rows
                        break
                    if len(e) > self.max_errors:
                        e.append(max_error_rule._exception_msg())
                        break
                if rix > (0 + self.skip_rows) or self.layout.no_header is True:
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


class CsvFile(_BaseFile):
    """
    CSV File class

    This class provides a way to validate the contents of a file against a
    Layout, and report any rule violations that exist. This is the primary
    means of using this package.

    :param layout: a Layout object which defines the fields that make up the
        data set, along with the various rules that should be applied to
        each one.
    :param skip_rows: the number of rows to skip before starting evaluation.
    :param max_errors: (optional) the maximum number of row errors to be
        collected before halting validation of rows and raising a FileError.
        This is used to prevent overly verbose (and mostly useless)
        validation reports from being generated. Defaults to 100. The error
        limit can overwritten (set to unlimited) by providing a value of -1.
    :param dialect: (optional) Controls csv dialect parsing.
    :param delimiter: (optional) Controls csv delimiter parsing.
    :param quotechar: (optional) Controls csv quote character parsing.
    """

    def __init__(self, layout: Union[Layout, dict], skip_rows=0, max_errors=100, **kwargs):
        x = {x: kwargs.pop(x, None) for x in ['dialect', 'delimiter', 'quotechar']}
        self.csv_kwargs = {k: v for k, v in x.items() if v}

        y = {y: kwargs.pop(y, None) for y in ['newline', 'encoding', 'errors']}
        self.file_kwargs = {k: v for k, v in y.items() if v}

        super().__init__(layout, skip_rows, max_errors, **kwargs)

    def _rows(self, file: Path):
        class Handler:
            def __init__(self, file_path: Path, csv_kwargs, file_kwargs):
                self.file_path = file_path
                self.csv_kwargs = csv_kwargs
                self.file_kwargs = file_kwargs
                self.file_kwargs['newline'] = self.file_kwargs.get('newline', '')

            def __enter__(self) -> Iterable:
                self.file_object = self.file_path.open(**self.file_kwargs)
                return csv.reader(self.file_object, **self.csv_kwargs)

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.file_object.close()

        return Handler(file, self.csv_kwargs, self.file_kwargs)


class ExcelFile(_BaseFile):
    """
    Excel File class

    This class provides a way to validate the contents of an Excel file against a
    Layout, and report any rule violations that exist. This is the primary
    means of using this package.

    :param layout: a Layout object which defines the fields that make up the
        data set, along with the various rules that should be applied to
        each one.
    :param skip_rows: the number of rows to skip before starting evaluation.
    :param max_errors: the maximum number of row errors to be
        collected before halting validation of rows and raising a FileError.
        This is used to prevent overly verbose (and mostly useless)
        validation reports from being generated. The error
        limit can be set to unlimited by providing a value of -1.

    """

    def __init__(self, layout: Union[Layout, Dict], skip_rows=0, max_errors=100, **kwargs):
        try:
            __import__('openpyxl')
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "openpyxl not available for import. You must install this"
                " package before you can use the ExcelFile class."
            )

        x = {x: kwargs.pop(x, None) for x in ['sheet']}
        self.excel_kwargs = {k: v for k, v in x.items() if v}
        # add ignore_ifs to the layout's fields when this gets constructed
        super().__init__(layout, skip_rows, max_errors, **kwargs)

    def _rows(self, file: Path):

        class Handler:
            def __init__(self, file_path, **kwargs):
                self.file_path = file_path
                self.excel_kwargs = kwargs

            def __enter__(self) -> Iterable:
                from openpyxl import load_workbook
                wb = load_workbook(file, read_only=False, data_only=True)
                sheet_name = self.excel_kwargs.get('sheet')
                ws = wb[sheet_name] if sheet_name else wb.active
                return ws.values

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        return Handler(file, **self.excel_kwargs)

    @staticmethod
    def _row_handler(row: list) -> List[str]:
        return ['' if x is None else str(x) for x in row]


class ParquetFile(_BaseFile):
    """
    Parquet File class

    This class provides a way to validate the contents of a Parquet file against a
    Layout, and report any rule violations that exist. This is accomplished by
    iterating rows within the file, and converting each to a string. This is incredibly
    inefficient, but it does mean that validation is applied to values in the file
    in exactly the same way as occurs with CSV and Excel files.

    Accuracy and consistency is preferred over efficiency in this case.

    :param layout: a Layout object which defines the fields that make up the
        data set, along with the various rules that should be applied to
        each one.
    :param max_errors: the maximum number of row errors to be
        collected before halting validation of rows and raising a FileError.
        This is used to prevent overly verbose (and mostly useless)
        validation reports from being generated. The error
        limit can be set to unlimited by providing a value of -1.

    """

    def __init__(self, layout: Union[Layout, Dict], max_errors=100, **kwargs):
        try:
            for mod in ('pandas', 'pyarrow'):
                __import__(mod)
        except ModuleNotFoundError:
            # noinspection PyUnboundLocalVariable
            raise ModuleNotFoundError(
                f"{mod} not available for import. You must install it to use {self.__class__.__name__}"
            )

        x = {x: kwargs.pop(x, None) for x in ['sheet']}
        self.parquet_kwargs = {k: v for k, v in x.items() if v}

        super().__init__(layout, max_errors=max_errors, **kwargs)

    def _rows(self, file: Path, sheet=None):
        class Handler:
            def __init__(self, file_path, **kwargs):
                self.file_path = file_path
                self.parquet_kwargs = kwargs

            def __enter__(self) -> Iterable:
                import pandas as pd
                df = pd.read_parquet(file)

                def gen():
                    yield df.columns.to_list()
                    for x in df.itertuples(index=False):
                        yield x

                return gen()

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        return Handler(file, **self.parquet_kwargs)

    @staticmethod
    def _row_handler(row: list) -> List[str]:
        import pandas as pd
        return ['' if pd.isna(x) else str(x) for x in row]
