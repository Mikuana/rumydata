class ValidationError(Exception):
    pass


class FileError(ValidationError):
    pass


class FileEncodingError(ValidationError):
    pass


class InvalidFileNameError(ValidationError):
    pass


class DataError(ValidationError):
    pass


class DateFormatError(ValidationError):
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


class NullValueError(ValidationError):
    pass


class ValueComparisonError(ValidationError):
    pass
