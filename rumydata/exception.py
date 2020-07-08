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
        if self.errors:
            return self.nested_exception_md()
        else:
            return self.exception_md()

    def nested_exception_md(self):
        return '\n'.join(
            [self.exception_md()] +
            ['  ' * y + x for x, y in self.flatten_exceptions(self.errors)]
        )

    def exception_md(self):
        return f' - {self.__class__.__name__}: {self.message}'

    @classmethod
    def flatten_exceptions(cls, errors, depth=0):
        """ Return error message fragment for markdown formatted output """
        depth += 1
        for el in errors:
            if isinstance(el, list) and not isinstance(el, (str, bytes)):
                yield from cls.flatten_exceptions(el, depth)
            else:
                yield str(el), depth


class FileError(UrNotMyDataError):
    pass


class RowError(UrNotMyDataError):
    pass


class CellError(UrNotMyDataError):
    pass


class NullValueError(CellError):
    message = 'value is blank/null'


if __name__ == '__main__':
    print(
        CellError('col6', [NullValueError(), NullValueError()])
    )
