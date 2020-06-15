import codecs
import csv
import re
import typing as t
from pathlib import Path

from rumydata import exception
from rumydata import rule
from rumydata.component import BaseValidator, Check, DataDefinition


class Text(BaseValidator):
    def __init__(self, max_length, min_length=None, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'String'
        self.descriptors['Max Length'] = f'{str(max_length)} characters'

        self.rules.append(rule.MaxChar(max_length))

        if min_length:
            self.descriptors['Min Length'] = f'{str(min_length)} characters'
            self.rules.append(rule.MinChar(min_length))


class Date(BaseValidator):
    def __init__(self, min_date: str = None, max_date: str = None, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Date'
        self.descriptors['Format'] = 'YYYY-MM-DD'

        self.rules.append(rule.CanBeDateIso())

        if max_date:
            self.descriptors['Max Date'] = f'{max_date}'
            self.rules.append(rule.DateLTE(max_date))

        if min_date:
            self.descriptors['Min Date'] = f'{min_date}'
            self.rules.append(rule.DateGTE(max_date))


class Currency(BaseValidator):
    def __init__(self, significant_digits: int, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Numeric'
        self.descriptors['Format'] = f'{"9" * (significant_digits - 2)}.99'
        self.descriptors['Max Length'] = f'{str(significant_digits)} digits'

        self.rules.append(rule.MaxDigit(significant_digits))
        self.rules.append(rule.NumericDecimals())


class Digit(BaseValidator):
    def __init__(self, max_length, min_length=None, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Numeric'
        self.descriptors['Format'] = f'{"0" * max_length}'
        self.descriptors['Max Length'] = f'{str(max_length)} digits'

        self.rules.append(rule.OnlyNumbers())
        self.rules.append(rule.MaxChar(max_length))

        if min_length:
            self.descriptors['Min Length'] = f'{str(min_length)} digits'
            self.rules.append(rule.MinChar(min_length))


class Integer(BaseValidator):
    def __init__(self, max_length, min_length=None, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Numeric'
        self.descriptors['Format'] = f'{"9" * max_length}'
        self.descriptors['Max Length'] = f'{str(max_length)} digits'

        self.rules.append(rule.CanBeInteger())
        self.rules.append(rule.NoLeadingZero())
        self.rules.append(rule.MaxDigit(max_length))

        if min_length:
            self.descriptors['Min Length'] = f'{str(max_length)} digits'
            self.rules.append(rule.MinDigit(min_length))


class Choice(BaseValidator):
    def __init__(self, valid_values: list, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Choice'
        self.descriptors['Choices'] = ','.join(valid_values)
        self.rules.append(rule.Choice(valid_values))


class Row(BaseValidator):
    def __init__(self, definition, **kwargs):
        super().__init__(**kwargs)
        expected_length = len(list(definition.keys()))

        self.rules.extend([
            rule.LengthLTE(expected_length),
            rule.LengthET(expected_length),
            rule.LengthGTE(expected_length)
        ])


class Header(BaseValidator):
    def __init__(self, definition, **kwargs):
        super().__init__(**kwargs)

        self.rules.extend([
            rule.HeaderColumnOrder(definition),
            rule.HeaderNoExtra(definition),
            rule.HeaderNoDuplicate(definition),
            rule.HeaderNoMissing(definition)
        ])


class Encoding(BaseValidator):
    def __init__(self, encoding='utf-8'):
        super().__init__()

        def try_encoding(x):
            try:
                with codecs.open(x, encoding=encoding, errors='strict'):
                    return True
            except UnicodeEncodeError:
                return False

        self.checks = [Check(
            try_encoding, exception.FileEncodingError, f'File is not encoded using {encoding}'
        )]


class File:
    errors = []
    data_definitions: t.List[DataDefinition] = None
    file_definition: dict = None

    def __init__(self, csv_file: t.Union[str, Path], data_definitions: t.List[DataDefinition]):
        self.data_definitions = data_definitions

        if isinstance(csv_file, str):
            csv_file = Path(csv_file)
        self.csv_file = Path(csv_file)

        if not self.csv_file.exists():
            raise FileNotFoundError(self.csv_file)
        self.validate_file()

        if not self.errors:  # if no errors found during file validation, move to validate data
            self.validate_data()

    def validate_file(self):
        no_match = True
        for d in self.data_definitions:
            if re.fullmatch(d.pattern, self.csv_file.name):
                self.file_definition = d.definition
                no_match = False

        if no_match:
            self.errors.append(
                exception.InvalidFileNameError(
                    f'No expected pattern matches file name. Valid patterns are:\n' +
                    '\n'.join([f'   - {x.pattern}' for x in self.data_definitions])
                )
            )

        self.errors.extend(Encoding().check_rules(self.csv_file))

    def validate_data(self):
        with open(self.csv_file) as f:
            names = list(self.file_definition.keys())
            types = list(self.file_definition.values())
            for rix, row in enumerate(csv.reader(f)):
                if rix == 0:  # if there are errors in header, skip data checks
                    self.errors.extend(
                        Header(self.file_definition).check_rules(row))
                    if self.errors:
                        break
                else:
                    row_check = Row(self.file_definition).check_rules(row)
                    if row_check:
                        self.errors.extend([
                            f'row {str(rix + 1)}: {x}' for x in row_check
                        ])
                        continue  # if there are errors in row, skip cell checks in row
                    for cix, cell in enumerate(row):
                        self.errors.extend([
                            f'row {str(rix + 1)} col {str(cix + 1)} ({names[cix]}): {x}'
                            for x in types[cix].check_rules(cell)
                        ])

    def summary(self):
        if self.errors:
            return f'Validation Failed for: {self.csv_file}\n' + (
                '\n'.join([f' - {x}' for x in self.errors])
            )
        else:
            return f'Validation Successful for: {self.csv_file} '
