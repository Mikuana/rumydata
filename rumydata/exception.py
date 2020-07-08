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
        return '\n' + self.md()

    def md(self, depth=0):
        txt = f'{"  " * depth} - {self.__class__.__name__}: {self.message}'
        if self.errors:
            txt = '\n'.join([txt] + [x for x in self.flatten_exceptions(self.errors, depth)])
        return txt

    @classmethod
    def flatten_exceptions(cls, errors, depth=0):
        """ Generate error message at appropriate indent for their nested depth """
        depth += 1
        for el in errors:
            if isinstance(el, list) and not isinstance(el, (str, bytes)):
                yield cls.flatten_exceptions(el, depth)
            elif isinstance(el, UrNotMyDataError):
                yield el.md(depth)
            else:
                raise Exception("You shouldn't be able to get here")


class FileError(UrNotMyDataError):
    pass


class RowError(UrNotMyDataError):
    def __init__(self, row: int, msg: str = None, errors: list = None):
        msg = f'row {str(row)}' + (f', {msg}' if msg else '')
        super().__init__(msg, errors)


class CellError(UrNotMyDataError):
    pass


class NullValueError(CellError):
    message = 'value is blank/null'


class NegativeValueError(CellError):
    message = "You're too negative"


if __name__ == '__main__':
    raise FileError(errors=[
        RowError(6, msg='bad row', errors=[CellError('col6', [
            NullValueError(errors=[NegativeValueError(errors=[NullValueError()])]), NullValueError()
        ])])
    ])
