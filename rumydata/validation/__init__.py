import csv
from pathlib import Path
from typing import Union

from rumydata import rule
from rumydata import exception
from rumydata.exception import FileError
from rumydata.validation.file import Layout


# from rumydata.validation.row import Header


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
                e = type(e)
                errors.append(e(
                    f'Error while attempting check if {r.explain()}')
                )
        return errors

    def digest(self):
        x = [f'{k}: {v}' if v else k for k, v in self.descriptors.items()]
        y = [x.explain() for x in self.rules]
        return x + y


class Cell(BaseValidator):
    def __init__(self, nullable=False, rules: list = None):
        super().__init__(rules)
        self.nullable = nullable

        if not self.nullable:
            self.rules.append(rule.NotNull)

    def __check__(self, value):
        # if data is nullable and value is empty, skip all checks
        if self.nullable and value == '':
            pass
        else:
            e = super().__check__(value)
            if e:
                return exception.CellError(errors=e)

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
            rule.LengthLTE(expected_length),
            rule.LengthET(expected_length),
            rule.LengthGTE(expected_length)
        ])

    def __check__(self, row: list, rix=-1):
        e = super().__check__(row)
        if e:  # if row errors are found, skip cell checks
            return exception.RowError(rix, errors=e)

        for cix, cell in enumerate(row):
            ce = self.types[cix].__check__(cell)
            if ce:
                e.append(ce)
        if e:
            return exception.RowError(rix, errors=e)

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

    def __check__(self, file: Union[str, Path]):
        p = Path(file) if isinstance(file, str) else file
        e = FileError(errors=list())
        e.errors.extend(super().__check__(p))  # check file-based rules first
        if e.errors:
            return e

        d = self.layout.definition
        with open(p) as f:
            names = list(d.keys())
            types = list(d.values())
            for rix, row in enumerate(csv.reader(f)):
                if rix == 0:  # abort checks if there are any header errors
                    errors.extend(Header(d).__check__(row))
                    if errors:
                        return errors
                else:
                    row_check = Row(d).__check__(row)
                    if row_check:
                        e.errors.extend([
                            f'row {str(rix + 1)}: {x}' for x in row_check
                        ])
                        continue  # if there are errors in row, skip cell checks
                    for cix, cell in enumerate(row):
                        e.errors.extend([
                            type(x)(
                                f'row {str(rix + 1)} col {str(cix + 1)} '
                                f'({names[cix]}): {x}'
                            )
                            for x in types[cix].__check__(cell)
                        ])
        if e.errors:
            return e
