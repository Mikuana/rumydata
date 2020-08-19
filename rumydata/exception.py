"""
rumydata exception module

This module contains specialized Exception classes which allow for aggregation
of all errors identified in a subject.

The majority of exceptions in this module are simple subclasses of the
UrNotMyDataError exception, which do nothing except rename the class. These
renames allow for more meaningful exception names to be associated with rules,
and allow for more specific checking of particular errors (especially useful
during testing).
"""


class UrNotMyDataError(Exception):
    """
    Base exception class for rumydata package

    This exception provides the structure for reporting nested exceptions in
    text format, in a way that the nested structure can be interpreted.
    """

    message: str = None

    def __init__(self, msg: str = None, errors: list = None):
        """
        Subclass constructor override for base exception

        This constructor allows a list of errors to be associated with this
        exception, in addition to providing a way to override the default
        message printed when this exception is raised.

        :param msg: a custom message to override the default with this exception
            is raised
        :param errors: a list of UrNotMyDataError exceptions which are nested
            within this object.
        """

        super().__init__(msg)
        self.message = msg or self.message
        self.errors = errors or []

    def __str__(self) -> str:
        """
        Exception string override

        This method overrides the default string and instead replaces it with
        the `md` method in this object. This allows simple string printing that
        can represent nested exceptions that exist in this object, and the
        exceptions that exist in those objects, and so on.
        """

        return '\n' + self.md()

    def md(self, depth=0) -> str:
        """
        Nested exception Markdown digest

        This method returns the complete tree of nested exceptions that exist in
        the errors property of this class in Markdown format, with indentation
        provided to indicate the relationship of nested exceptions.

        :param depth: an integer which indicates the level of indentation that
            an exception needs to represent its relationship in the nested
            structure. Do not call directly.
        :return: a string of nested exceptions in Markdown format, with
            indentation providing visual indicator of nested structure.
        """

        txt = f'{"  " * depth} - {self.__class__.__name__[:-5]}: {self.message}'
        if self.errors:
            txt = '\n'.join([txt] + [x for x in self.flatten_md(self.errors, depth)])
        return txt

    @classmethod
    def flatten_md(cls, errors, depth=0):
        """
        Nested exception Markdown generator

        Recurse through nested exceptions and continue to yield exceptions until
        exhausted.
        """

        depth += 1
        for el in errors:
            if isinstance(el, list) and not isinstance(el, (str, bytes)):
                yield cls.flatten_md(el, depth)
            elif issubclass(el.__class__, UrNotMyDataError):
                yield el.md(depth)
            else:
                yield UrNotMyDataError(el).md(depth)


class FileError(UrNotMyDataError):
    """ File Error exception """

    def __init__(self, file, msg=None, errors: list = None):
        """
        File error constructor.

        :param file: name of the file reported with the error message.
        :param msg: a custom message to use when reporting errors in the file.
        :param errors: a list of errors contained in the file.
        """

        message = file
        message += f'; {msg}' if msg else ''
        super().__init__(message, errors)


class ColumnError(UrNotMyDataError):
    """ Column Error Exception """

    def __init__(self, msg=None, errors: list = None):
        """
        Column error constructor.

        :param msg: a custom message to use when reporting errors in the column.
        :param errors: a list of errors contained in the column.
        """
        super().__init__(msg, errors)


class RowError(UrNotMyDataError):
    """ Row Error exception """

    def __init__(self, index: int, msg=None, errors: list = None, **kwargs):
        """
        Row Error constructor.

        :param index: row number (using zero-indexing). Reported with the
            exception message to allow identification of the row.
        :param msg: a custom message to use when reporting errors in this row.
        :param errors: a list of errors contained in this row
        :param zero_index: specify whether to use zero-indexing when reporting
            row number. If True, the index is reported as provided. If False,
            the index is increased by one.
        """

        message = f'{str(index + (0 if kwargs.get("zero_index") else 1))}'
        message += f'; {msg}' if msg else ''
        super().__init__(message, errors)


class CellError(UrNotMyDataError):
    """ Cell Error exception """

    def __init__(self, index: int, msg=None, errors: list = None, **kwargs):
        """
        Cell Error constructor

        :param index: column number (using zero-indexing). Reported with the
            exception message to allow identification of the column.
        :param msg: a custom message to use when reporting errors in this cell.
        :param errors: a list of errors contained in this cell.
        :param zero_index: specify whether to use zero-indexing when reporting
            column number. If True, the index is reported as provided. If False,
            the index increased by one.
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


class NullValueError(UrNotMyDataError):
    message = 'value is blank/null'


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
