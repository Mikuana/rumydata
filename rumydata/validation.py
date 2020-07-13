import csv
from pathlib import Path
from re import compile
from typing import Union, Pattern

from rumydata import exception, rule
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


class BaseValidator:
    def __init__(self, rules: list = None):
        self.rules = rules or []
        self.descriptors = {}

    def __check__(self, value):
        errors = []
        for r in self.rules:
            # noinspection PyBroadException
            try:
                if not r.evaluator()(value):
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

    def list_errors(self, value):
        return list(self.flatten_exceptions(self.__check__(value)))

    def has_error(self, value, error):
        return error in [x.__class__ for x in self.list_errors(value)]

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
            self.rules.append(rule.NotNull)

    def __check__(self, value, cix=-1, **kwargs):
        # if data is nullable and value is empty, skip all checks
        if self.nullable and value == '':
            pass
        else:
            e = super().__check__(value)
            if e:
                return exception.CellError(cix, errors=e, **kwargs)

    def check(self, value):
        errors = self.__check__(value)
        assert not errors, str(errors)

    def digest(self):
        dig = super().digest()
        if self.nullable:
            dig.append('Nullable')
        return dig


class Row(BaseValidator):
    def __init__(self, layout: Layout, **kwargs):
        super().__init__(**kwargs)

        self.names = list(layout.definition.keys())
        self.types = list(layout.definition.values())

        expected_length = len(layout.definition)
        self.rules.extend([
            rule.RowLengthLTE(expected_length),
            rule.RowLengthGTE(expected_length),
        ])

    def __check__(self, row: list, rix=-1):
        e = super().__check__(row)
        if e:  # if row errors are found, skip cell checks
            return exception.RowError(rix, errors=e)

        for cix, cell in enumerate(row):
            ce = self.types[cix].__check__(cell, cix, rix=rix, name=self.names[cix])
            if ce:
                e.append(ce)
        if e:
            return exception.RowError(rix, errors=e)

    def check(self, row):
        errors = self.__check__(row)
        assert not errors, str(errors)


class Header(BaseValidator):
    def __init__(self, layout: Layout, **kwargs):
        super().__init__(**kwargs)

        self.rules.extend([
            rule.HeaderColumnOrder(layout.definition),
            rule.HeaderNoExtra(layout.definition),
            rule.HeaderNoDuplicate(layout.definition),
            rule.HeaderNoMissing(layout.definition)
        ])

    def __check__(self, row: list):
        e = super().__check__(row)
        if e:  # if row errors are found, skip cell checks
            return exception.RowError(1, errors=e)

    def check(self, row):
        errors = self.__check__(row)
        assert not errors, str(errors)


class File(BaseValidator):
    def __init__(self, layout: Layout, **kwargs):
        super().__init__(**kwargs)
        self.layout = layout

        self.rules.extend([
            rule.FileExists(),
            rule.FileNameMatchesPattern(self.layout.pattern),
        ])

    def __check__(self, filepath: Union[str, Path]):
        p = Path(filepath) if isinstance(filepath, str) else filepath
        e = super().__check__(p)  # check file-based rules first
        if e:
            return FileError(errors=e)

        with open(p) as f:
            hv, rv = Header(self.layout), Row(self.layout)
            for rix, row in enumerate(csv.reader(f)):
                if rix == 0:  # abort checks if there are any header errors
                    re = hv.__check__(row)
                else:
                    re = rv.__check__(row, rix)
                if re:
                    e.append(re)
        if e:
            return FileError(errors=e)

    def check(self, file_path):
        errors = self.__check__(file_path)
        assert not errors, str(errors)
