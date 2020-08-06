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


class ValueComparisonError(UrNotMyDataError):
    pass


class FileUrNotMyDataError(UrNotMyDataError):
    pass


class FilePatternError(UrNotMyDataError):
    pass


class FileError(UrNotMyDataError):
    def __init__(self, file, msg=None, errors: list = None):
        """
        :param file: name of the files that will be reported with the error message.
        :param msg: a custom message to include when reporting errors in this files.
        :param errors: a list of errors contained in this files.
        """
        message = file
        message += f'; {msg}' if msg else ''
        super().__init__(message, errors)


class ColumnError(UrNotMyDataError):
    def __init__(self, msg=None, errors: list = None, **kwargs):
        super().__init__(msg, errors)


class RowError(UrNotMyDataError):
    def __init__(self, index: int, msg=None, errors: list = None, **kwargs):
        """
        :param index: row number (using zero-indexing).
        :param msg: a custom message to include when reporting errors in this row
        :param errors: a list of errors contained in this row
        :param zero_index: specify whether to use zero-indexing when reporting row number.
        If True, the index is reported as provided. If False, the index increased
        by one.
        """
        message = f'{str(index + (0 if kwargs.get("zero_index") else 1))}'
        message += f'; {msg}' if msg else ''
        super().__init__(message, errors)


class CellError(UrNotMyDataError):
    def __init__(self, index: int, msg=None, errors: list = None, **kwargs):
        """
        :param index: column number (using zero-indexing).
        :param msg: a custom message to include when reporting errors in this cell
        :param errors: a list of errors contained in this cell
        :param zero_index: specify whether to use zero-indexing when reporting column number.
        If True, the index is reported as provided. If False, the index increased
        by one.
        """
        message = ''
        offset = 0 if kwargs.get("zero_index") else 1
        if kwargs.get('rix'):
            message = str(kwargs.get('rix') + offset) + ','

        message += f'{str(index + offset)}'
        if kwargs.get("name"):
            message += f' ({kwargs.get("name")})'
        message += f'; {msg}' if msg else ''
        super().__init__(message, errors)


class NullValueError(UrNotMyDataError):
    message = 'value is blank/null'


class NegativeValueError(CellError):
    message = "You're too negative"


class MaxExceededError(UrNotMyDataError):
    pass


class ColumnComparisonError(UrNotMyDataError):
    pass


class RowComparisonError(UrNotMyDataError):
    pass


class CharacterError(UrNotMyDataError):
    pass


class DuplicateValueError(UrNotMyDataError):
    pass


class NoRulesDefinedError(UrNotMyDataError):
    pass
