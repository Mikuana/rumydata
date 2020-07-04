from typing import List


class ValidationError(Exception):
    pass


# class FileError(ValidationError):
#     pass
#

class FileEncodingError(ValidationError):
    pass


class InvalidFileNameError(ValidationError):
    pass


class DataError(ValidationError):
    pass


class DateFormatError(ValidationError):
    pass


class ConversionError(ValidationError):
    pass


class CurrencyPatternError(ValidationError):
    pass


class DataLengthError(ValidationError):
    pass


class LeadingZeroError(ValidationError):
    pass


class InvalidChoiceError(ValidationError):
    pass


class MissingColumnError(ValidationError):
    pass


class UnexpectedColumnError(ValidationError):
    pass


class DuplicateColumnError(ValidationError):
    pass


class RowLengthError(ValidationError):
    pass


class NotEnoughFieldsError(ValidationError):
    pass


class TooManyFieldsError(ValidationError):
    pass


#
# class NullValueError(ValidationError):
#     pass


class ValueComparisonError(ValidationError):
    pass


class FileValidationError(ValidationError):
    pass


class FilePatternError(ValidationError):
    pass


class UrNotMyDataError(Exception):
    message: str = None

    def __init__(self, msg: str = None, errors: list = None):
        super().__init__(msg)
        self.message = msg or self.message
        self.errors = errors or []

    def __str__(self):
        return f' - {self.__class__.__name__}: {self.message}' + ('\n'.join(str(x) for x in self.errors) if self.errors else '')


class FileError(UrNotMyDataError):
    pass


class RowError(UrNotMyDataError):
    pass


class CellError(UrNotMyDataError):
    pass


class NullValueError(CellError):
    message = 'value is blank/null'


if __name__ == '__main__':
    print(RowError('row 5'))
    print(CellError('col 6 (MyColumn)'))
    print(NullValueError())
    print()

    print(
        CellError('col6', [NullValueError()])
    )
