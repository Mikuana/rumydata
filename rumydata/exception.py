class UrNotMyDataError(Exception):
    message: str = None

    def __init__(self, msg: str = None, errors: list = None):
        super().__init__(msg)
        self.message = msg or self.message
        self.errors = errors or []

    def __str__(self):
        return '\n' + self.md()

    def md(self, depth=0):
        txt = f'{"  " * depth} - {self.__class__.__name__[:-5]}: {self.message}'
        if self.errors:
            txt = '\n'.join([txt] + [x for x in self.flatten_md(self.errors, depth)])
        return txt

    @classmethod
    def flatten_md(cls, errors, depth=0):
        """ Generate error message at appropriate indent for their nested depth """
        depth += 1
        for el in errors:
            if isinstance(el, list) and not isinstance(el, (str, bytes)):
                yield cls.flatten_md(el, depth)
            elif issubclass(el.__class__, UrNotMyDataError):
                yield el.md(depth)
            else:
                yield UrNotMyDataError(el).md(depth)


class InvalidFileNameError(UrNotMyDataError):
    pass


class DataError(UrNotMyDataError):
    pass


class DateFormatError(UrNotMyDataError):
    pass


class ConversionError(UrNotMyDataError):
    pass


class CurrencyPatternError(UrNotMyDataError):
    pass


class LengthError(UrNotMyDataError):
    pass


class LeadingZeroError(UrNotMyDataError):
    pass


class InvalidChoiceError(UrNotMyDataError):
    pass


class MissingColumnError(UrNotMyDataError):
    pass


class UnexpectedColumnError(UrNotMyDataError):
    pass


class DuplicateColumnError(UrNotMyDataError):
    pass


class RowLengthError(UrNotMyDataError):
    pass


class NotEnoughFieldsError(UrNotMyDataError):
    pass


class TooManyFieldsError(UrNotMyDataError):
    pass


#
# class NullValueError(UrNotMyDataError):
#     pass


class ValueComparisonError(UrNotMyDataError):
    pass


class FileUrNotMyDataError(UrNotMyDataError):
    pass


class FilePatternError(UrNotMyDataError):
    pass


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
