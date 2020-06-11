import codecs
import csv
import re
import typing as t
from datetime import datetime
from pathlib import Path

from rumydata import exception
from rumydata.component import BaseValidator, Check, DataDefinition


class Text(BaseValidator):
    def __init__(self, max_length, min_length=None, **kwargs):
        super().__init__(**kwargs)

        self.attributes['Type'] = 'String'
        self.attributes['Max Length'] = f'{str(max_length)} characters'

        self.checks.append(Check(
            lambda x: len(x) <= max_length, exception.DataLengthError,
            f'Text value exceeds max length {str(max_length)}'
        ))

        if min_length:
            self.attributes['Min Length'] = f'{str(min_length)} characters'

            self.checks.append(Check(
                lambda x: len(x) >= min_length, exception.DataLengthError,
                f'Text value does not meet minimum length {str(min_length)}'
            ))


class Date(BaseValidator):
    def __init__(self, min_year=1900, max_year=2100, **kwargs):
        super().__init__(**kwargs)

        self.attributes['Type'] = 'Date'
        self.attributes['Format'] = 'YYYY-MM-DD'
        self.attributes['Min Year'] = f'{str(min_year)}'
        self.attributes['Max Year'] = f'{str(max_year)}'

        self.checks.append(Check(
            lambda x: re.fullmatch(r'\d{4}-\d{2}-\d{2}', x), exception.DateFormatError,
            'Date value does not look like YYYY-MM-DD format'
        ))

        self.checks.append(Check(
            lambda x: datetime.strptime(x, '%Y-%m-%d'), exception.DataError,
            'Date value is not a valid date'
        ))

        self.checks.append(Check(
            lambda x: datetime.strptime(x, '%Y-%m-%d').year >= min_year, exception.DataError,
            f'Date value is before minimum year {str(min_year)}'
        ))

        self.checks.append(Check(
            lambda x: datetime.strptime(x, '%Y-%m-%d').year <= max_year, exception.DataError,
            f'Date value is after maximum year {str(max_year)}'
        ))


class Currency(BaseValidator):
    def __init__(self, significant_digits: int, **kwargs):
        super().__init__(**kwargs)

        self.attributes['Type'] = 'Numeric'
        self.attributes['Format'] = f'{"9" * (significant_digits - 2)}.99'
        self.attributes['Max Length'] = f'{str(significant_digits)} digits'

        self.checks.append(Check(
            lambda x: float(x) <= int('9' * significant_digits), exception.DataError,
            f'Currency value is too large'
        ))
        self.checks.append(Check(
            lambda x: len(x) <= significant_digits + 1, exception.DataLengthError,
            f'Currency value is not less than {str(significant_digits)} significant digits'
        ))
        self.checks.append(Check(
            lambda x: re.fullmatch(r'-?\d+(\.\d{1,2})?', x), exception.CurrencyPatternError,
            f'Currency pattern is not a whole number with a maximum of two digits past decimal'
        ))


class Digit(BaseValidator):
    def __init__(self, max_length, min_length=None, **kwargs):
        super().__init__(**kwargs)

        self.attributes['Type'] = 'Numeric'
        self.attributes['Format'] = f'{"0" * max_length}'
        self.attributes['Max Length'] = f'{str(max_length)} digits'

        self.checks.append(Check(
            lambda x: re.fullmatch(r'\d+', x), exception.DataError,
            'Digit value is not made exclusively of numbers'
        ))

        self.checks.append(Check(
            lambda x: len(x) <= max_length, exception.DataLengthError,
            f'Digit value exceeds max length {str(max_length)}'
        ))

        if min_length:
            self.attributes['Min Length'] = f'{str(min_length)} digits'
            self.checks.append(Check(
                lambda x: len(x) >= min_length, exception.DataLengthError,
                f'Digit value does not meet minimum length {str(min_length)}'
            ))


class Integer(BaseValidator):
    def __init__(self, max_length, min_length=None, **kwargs):
        super().__init__(**kwargs)

        self.attributes['Type'] = 'Numeric'
        self.attributes['Format'] = f'{"9" * max_length}'
        self.attributes['Max Length'] = f'{str(max_length)} digits'

        self.checks.append(Check(
            lambda x: isinstance(int(x), int), exception.DataError,
            'Integer value cannot be coerced into an integer'
        ))
        self.checks.append(Check(
            lambda x: re.fullmatch(r'-?(0|([1-9]\d*))', x), exception.LeadingZeroError,
            'Integer value does not start with non-zero digit'
        ))

        self.checks.append(Check(
            lambda x: len(x[1:] if x.startswith('-') else x) <= max_length,
            exception.DataLengthError, f'Integer value exceeds max length {str(max_length)}'
        ))

        if min_length:
            self.attributes['Min Length'] = f'{str(max_length)} digits'
            self.checks.append(Check(
                lambda x: len(x[1:] if x.startswith('-') else x) >= min_length,
                exception.DataLengthError,
                f'Integer value does not meet minimum length {str(min_length)}'
            ))


class Choice(BaseValidator):
    def __init__(self, valid_values: list, **kwargs):
        super().__init__(**kwargs)

        self.attributes['Type'] = 'Choice'
        self.attributes['Choices'] = ','.join(valid_values)

        self.checks.append(Check(
            lambda x: x in valid_values, exception.InvalidChoiceError,
            f'Choice value is not one of: {valid_values}'
        ))


class Row(BaseValidator):
    def __init__(self, definition, **kwargs):
        super().__init__(**kwargs)

        self.checks.append(Check(
            lambda x: len(x) == len(list(definition.keys())), exception.RowLengthError,
            f'Row length not equal to {str(len(list(definition.keys())))}'
        ))

        self.checks.append(Check(
            lambda x: len(x) >= len(list(definition.keys())), exception.NotEnoughFieldsError,
            f'Row length is less than {str(len(list(definition.keys())))}'
        ))

        self.checks.append(Check(
            lambda x: len(x) <= len(list(definition.keys())), exception.TooManyFieldsError,
            f'Row length is greater than {str(len(list(definition.keys())))}'
        ))


class Header(BaseValidator):
    def __init__(self, definition, **kwargs):
        super().__init__(**kwargs)

        self.checks.append(Check(
            lambda x: len(x) == len(list(definition.keys())), exception.RowLengthError,
            f'Header row count not equal to {str(len(list(definition.keys())))}'
        ))

        self.checks.append(Check(
            lambda x: all([y in definition for y in x]),
            exception.UnexpectedColumnError, 'Header row includes an unexpected column'
        ))

        self.checks.append(Check(
            lambda x: all([y in x for y in definition]),
            exception.MissingColumnError, 'Header row missing an expected column'
        ))

        self.checks.append(Check(
            lambda x: x == list(definition),
            exception.DataError, 'Header row may be out of expected order'
        ))

        self.checks.append(Check(
            lambda x: len(x) == len(set(x)),
            exception.DuplicateColumnError, 'Header row contains duplicate value'
        ))


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

        self.errors.extend(Encoding().check_errors(self.csv_file))

    def validate_data(self):
        with open(self.csv_file) as f:
            names = list(self.file_definition.keys())
            types = list(self.file_definition.values())
            for rix, row in enumerate(csv.reader(f)):
                if rix == 0:  # if there are errors in header, skip data checks
                    self.errors.extend(
                        Header(self.file_definition).check_errors(row))
                    if self.errors:
                        break
                else:
                    row_check = Row(self.file_definition).check_errors(row)
                    if row_check:
                        self.errors.extend([
                            f'row {str(rix + 1)}: {x}' for x in row_check
                        ])
                        continue  # if there are errors in row, skip cell checks in row
                    for cix, cell in enumerate(row):
                        self.errors.extend([
                            f'row {str(rix + 1)} col {str(cix + 1)} ({names[cix]}): {x}'
                            for x in types[cix].check_errors(cell)
                        ])

    def summary(self):
        if self.errors:
            return f'Validation Failed for: {self.csv_file}\n' + (
                '\n'.join([f' - {x}' for x in self.errors])
            )
        else:
            return f'Validation Successful for: {self.csv_file} '
