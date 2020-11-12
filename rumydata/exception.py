"""
Exception module

This module contains specialized Exception classes which allow for aggregation
of all errors identified in a subject. These exceptions provide the structure to
collect multiple exceptions at varying levels within a validation process, and
display them in a meaningful way.
"""


def debug():
    """
    Exception debug mode control

    A switch to control exception message sanitation. This is a static
    function which will always return False. In order to enable debug mode, you
    must monkey patch this function using the mock library. This is made to
    intentionally be inconvenient in order to prevent accidental disclosure of
    data in exception logs through overuse of the debug mode.

    This method is used at runtime by the base _check method. In order to enable
    debugging, you must include a patch statement before calling a check. It is
    recommended that you do this with a context handler to ensure appropriate
    behavior of the patch.

    example::

        from unittest.mock import patch
        from rumydata import field

        with patch('rumydata.exception.debug', return_value=True):
            field.Integer(1).check_cell(None)
    """
    return False


class UrNotMyDataError(Exception):
    """
    Base exception class for rumydata package

    This exception provides the structure for reporting nested exceptions in
    text format, in a way that the nested structure can be interpreted.

    The constructor allows a list of errors to be associated with this
    exception, in addition to providing a way to override the default
    message printed when this exception is raised.

    :param msg: a custom message to override the default with this exception
        is raised
    :param errors: a list of UrNotMyDataError exceptions which are nested
        within this object.
    """

    _message: str = None

    def __init__(self, msg: str = None, errors: list = None):
        super().__init__(msg)
        self._message = msg or self._message
        self._errors = errors or []

    def __str__(self) -> str:
        """
        Exception string override

        This method overrides the default string and instead replaces it with
        the `md` method in this object. This allows simple string printing that
        can represent nested exceptions that exist in this object, and the
        exceptions that exist in those objects, and so on.
        """

        return '\n' + self._md()

    def _md(self, depth=0) -> str:
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

        txt = f'{"  " * depth} - {self.__class__.__name__[:-5]}: {self._message}'
        if self._errors:
            txt = '\n'.join([txt] + [x for x in self._flatten_md(self._errors, depth)])
        return txt

    @classmethod
    def _flatten_md(cls, errors, depth=0):
        """
        Nested exception Markdown generator

        Recurse through nested exceptions and continue to yield exceptions until
        exhausted.
        """

        depth += 1
        for el in errors:
            yield el._md(depth)


class FileError(UrNotMyDataError):
    """
    File Error exception

    :param file: name of the file reported with the error message.
    :param msg: a custom message to use when reporting errors in the file.
    :param errors: a list of errors contained in the file.
    """

    def __init__(self, file, msg=None, errors: list = None):
        message = file
        message += f'; {msg}' if msg else ''
        super().__init__(message, errors)


class ColumnError(UrNotMyDataError):
    """
    Column Error Exception

    :param msg: a custom message to use when reporting errors in the column.
    :param errors: a list of errors contained in the column.
    """

    def __init__(self, index: int, msg=None, errors: list = None, **kwargs):
        message = ''
        offset = 0 if kwargs.get("zero_index") else 1

        message += f'{str(index + offset)}'
        if kwargs.get("name"):
            message += f' ({kwargs.get("name")})'
        message += f'; {msg}' if msg else ''
        super().__init__(message, errors)


class RowError(UrNotMyDataError):
    """
    Row Error exception

    :param index: row number (using zero-indexing). Reported with the
        exception message to allow identification of the row.
    :param msg: a custom message to use when reporting errors in this row.
    :param errors: a list of errors contained in this row
    :param zero_index: specify whether to use zero-indexing when reporting
        row number. If True, the index is reported as provided. If False,
        the index is increased by one.
    """

    def __init__(self, index: int, msg=None, errors: list = None, **kwargs):
        message = f'{str(index + (0 if kwargs.get("zero_index") else 1))}'
        message += f'; {msg}' if msg else ''
        super().__init__(message, errors)


class CellError(UrNotMyDataError):
    """
    Cell Error exception

    :param index: column number (using zero-indexing). Reported with the
        exception message to allow identification of the column.
    :param msg: a custom message to use when reporting errors in this cell.
    :param errors: a list of errors contained in this cell.
    :param zero_index: specify whether to use zero-indexing when reporting
        column number. If True, the index is reported as provided. If False,
        the index increased by one.
    """

    def __init__(self, index: int, msg=None, errors: list = None, **kwargs):
        message = ''
        offset = 0 if kwargs.get("zero_index") else 1
        if kwargs.get('rix'):
            message = str(kwargs.get('rix') + offset) + ','

        message += f'{str(index + offset)}'
        if kwargs.get("name"):
            message += f' ({kwargs.get("name")})'
        message += f'; {msg}' if msg else ''
        super().__init__(message, errors)


class PreProcessingError(UrNotMyDataError):
    """
    Data Preprocessing Exception

    Thrown specifically when the data pre-processing step for a subject fails.
    This is treated differently than the exceptions thrown by all fields, since
    pre-processing exceptions prevent any further rules from being checked.
    """
