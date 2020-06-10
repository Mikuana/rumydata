class FileError(Exception):
    pass


class InvalidFileNameError(FileError):
    pass


class DataError(Exception):
    pass


class DateFormatError(Exception):
    pass


class CurrencyPatternError(Exception):
    pass


class DataLengthError(Exception):
    pass


class LeadingZeroError(Exception):
    pass


class InvalidChoiceError(Exception):
    pass


class MissingColumnError(Exception):
    pass


class UnexpectedColumnError(Exception):
    pass


class DuplicateColumnError(Exception):
    pass
