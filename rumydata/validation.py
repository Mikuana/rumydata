import csv
from pathlib import Path
from re import compile
from typing import Union, Pattern

import rumydata.rule.base
import rumydata.rule.cell
import rumydata.rule.file
import rumydata.rule.header
from rumydata import exception
from rumydata.exception import FileError


class Layout:
    def __init__(self, definition: dict, pattern: Union[str, Pattern] = None, **kwargs):
        """
        Defines the layout of a tabular file.

        :param definition: dictionary of column names with DataType definitions
        :param pattern: an optional regex pattern - provided as either a string or
        a re.Pattern class - which will be used to determine if a file matches an
        expected naming schema. This is necessary when your data set includes multiple,
        as it allows the package to determine which definition should be used to
        validate file.
        """
        if isinstance(pattern, str):
            self.pattern = compile(pattern)
        elif isinstance(pattern, Pattern):
            self.pattern = pattern
        elif not pattern:
            self.pattern = compile(r'.+')

        self.definition = definition

        self.title = kwargs.get('title')

    def digest(self):
        return [[f'Name: {k}', *v.digest()] for k, v in self.definition.items()]

    def markdown_digest(self):
        fields = f'# {self.title}' + '\n\n' if self.title else ''
        fields += '\n'.join([
            f' - **{k}**' + ''.join(['\n   - ' + x for x in v.digest()])
            for k, v in self.definition.items()
        ])
        return fields

    def check_file(self, file: Union[str, Path], **kwargs):
        File(self, **kwargs).check(file)

    def comparison_columns(self):
        compares = set()
        for v in self.definition.values():
            compares.update(v.comparison_columns())
        return compares


class BaseValidator:
    def __init__(self, rules: list = None):
        self.rules = rules or []
        self.descriptors = {}

    def __check__(self, value, **kwargs):
        errors = []
        for r in self.rules:

            # noinspection PyBroadException
            try:
                if issubclass(type(r), rumydata.rule.base.ColumnsRule):
                    e = r.evaluator()(value, kwargs.get('compare')[r.compare_to])
                else:
                    e = r.evaluator()(value)

                if not e:
                    errors.append(r.exception_msg())
            except Exception as e:  # get type, and rewrite safe message
                errors.append(r.exception_class(
                    f'raised {e.__class__.__name__} while checking if value {r.explain()}')
                )
        return errors

    def digest(self):
        x = [f'{k}: {v}' if v else k for k, v in self.descriptors.items()]
        y = [x.explain() for x in self.rules]
        return x + y

    def list_errors(self, value, **kwargs):
        return list(self.flatten_exceptions(self.__check__(value, **kwargs)))

    def has_error(self, value, error, **kwargs):
        return error in [x.__class__ for x in self.list_errors(value, **kwargs)]

    @classmethod
    def flatten_exceptions(cls, error):
        if isinstance(error, list):
            for el in error:
                yield cls.flatten_exceptions(el)
        elif issubclass(error.__class__, exception.UrNotMyDataError):
            yield error
            for el in error.errors:
                for x in cls.flatten_exceptions(el):
                    yield x
        else:
            yield error


class Cell(BaseValidator):
    def __init__(self, nullable=False, rules: list = None):
        super().__init__(rules)
        self.nullable = nullable

        if not self.nullable:
            self.rules.append(rumydata.rule.cell.NotNull)

    def __check__(self, value, cix=-1, **kwargs):
        # if data is nullable and value is empty, skip all checks
        if self.nullable and value == '':
            pass
        else:
            e = super().__check__(value, compare=kwargs.get('compare'))
            if e:
                return exception.CellError(cix, errors=e, **kwargs)

    def check(self, value, **kwargs):
        errors = self.__check__(value, **kwargs)
        assert not errors, str(errors)

    def digest(self):
        dig = super().digest()
        if self.nullable:
            dig.append('Nullable')
        return dig

    def comparison_columns(self):
        compares = set()
        for r in self.rules:
            if issubclass(type(r), rumydata.rule.base.ColumnsRule):
                compares.add(r.compare_to)
        return compares


class Row(BaseValidator):
    def __init__(self, layout: Layout, **kwargs):
        super().__init__(**kwargs)
        self.definition = layout.definition

        self.rules.extend([
            rumydata.rule.cell.RowLengthLTE(len(self.definition)),
            rumydata.rule.cell.RowLengthGTE(len(self.definition))
        ])

    def __check__(self, row: list, rix=-1):
        e = super().__check__(row)
        if e:  # if row errors are found, skip cell checks
            return exception.RowError(rix, errors=e)

        row = dict(zip(self.definition.keys(), row))

        for cix, (name, val) in enumerate(row.items()):
            t = self.definition[name]
            comp = {k: row[k] for k in t.comparison_columns()}
            ce = t.__check__(val, cix, rix=rix, name=name, compare=comp)
            if ce:
                e.append(ce)
        if e:
            return exception.RowError(rix, errors=e)

    def check(self, row, **kwargs):
        errors = self.__check__(row, **kwargs)
        assert not errors, str(errors)


class Header(BaseValidator):
    def __init__(self, layout: Layout, **kwargs):
        super().__init__(**kwargs)

        self.rules.extend([
            rumydata.rule.header.HeaderColumnOrder(layout.definition),
            rumydata.rule.header.HeaderNoExtra(layout.definition),
            rumydata.rule.header.HeaderNoDuplicate(layout.definition),
            rumydata.rule.header.HeaderNoMissing(layout.definition)
        ])

    def __check__(self, row: list, **kwargs):
        e = super().__check__(row)
        if e:  # if row errors are found, skip cell checks
            return exception.RowError(0, errors=e)

    def check(self, row):
        errors = self.__check__(row)
        assert not errors, str(errors)


class File(BaseValidator):
    def __init__(self, layout: Layout, max_errors=100, **kwargs):
        # pop any csv reader kwargs for later use
        x = {x: kwargs.pop(x, None) for x in ['dialect', 'delimiter', 'quotechar']}
        self.csv_kwargs = {k: v for k, v in x.items() if v}
        super().__init__(**kwargs)

        self.max_errors = max_errors
        self.layout = layout
        self.rules.extend([
            rumydata.rule.file.FileExists(),
            rumydata.rule.file.FileNameMatchesPattern(self.layout.pattern),
        ])

    def __check__(self, filepath: Union[str, Path], **kwargs):
        p = Path(filepath) if isinstance(filepath, str) else filepath
        e = super().__check__(p)  # check file-based rules first
        if e:
            return FileError(file=filepath, errors=e)

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
                        e.append(exception.MaxExceededError(m))
                        break
        if e:
            return FileError(file=p.name, errors=e)

    def check(self, file_path):
        errors = self.__check__(file_path)
        assert not errors, str(errors)
