import re
from datetime import datetime
from pathlib import Path
from typing import Union, List

from rumydata import exception as ex


class Rule:
    """ Base class for defining data type rules """
    exception_class = ex.UrNotMyDataError

    def evaluator(self):
        """
        :return: a function which expects to evaluate to True, if the value
        provided to the function meets the rule.
        """
        pass

    def exception_msg(self):
        """
        :return: a sanitized error message which is specific to the function,
        contains no direct link to the value that was checked.
        """
        return self.exception_class(self.explain())

    def explain(self) -> str:
        """
        :return: an explanation of the rule that is applied
        """
        pass


class NotNull(Rule):
    exception_class = ex.NullValueError

    @classmethod
    def evaluator(cls):
        return lambda x: x != ''

    @classmethod
    def exception_msg(cls):
        return cls.exception_class(cls.explain())

    @classmethod
    def explain(cls):
        return 'cannot be empty/blank'


class ExactChar(Rule):
    exception_class = ex.LengthError

    def __init__(self, exact_length):
        self.exact_length = exact_length

    def evaluator(self):
        return lambda x: len(x) == self.exact_length

    def explain(self):
        return f'must be exactly {str(self.exact_length)} characters'


class MinChar(Rule):
    exception_class = ex.LengthError

    def __init__(self, min_length):
        self.min_length = min_length

    def evaluator(self):
        return lambda x: len(x) >= self.min_length

    def explain(self):
        return f'must be at least {str(self.min_length)} characters'


class MaxChar(Rule):
    exception_class = ex.LengthError

    def __init__(self, max_length):
        self.max_length = max_length

    def evaluator(self):
        return lambda x: len(x) <= self.max_length

    def explain(self):
        return f'must be no more than {str(self.max_length)} characters'


class Choice(Rule):
    exception_class = ex.InvalidChoiceError

    def __init__(self, choices: list):
        self.choices = choices

    def evaluator(self):
        return lambda x: x in self.choices

    def explain(self):
        return f'must be one of {self.choices}'


class MinDigit(Rule):
    """
    Check that count of characters, after removing all non-digits, meets or
    exceeds the specified minimum. Used to evaluate length of significant digits
    in numeric strings that might contain formatting.
    """
    exception_class = ex.LengthError

    def __init__(self, min_length):
        self.min_length = min_length

    def evaluator(self):
        return lambda x: len(re.sub(r'[^\d]', '', x)) >= self.min_length

    def explain(self):
        return f'must have at least {str(self.min_length)} digit characters'


class MaxDigit(Rule):
    """
    Check that count of characters, after removing all non-digits, is less than
    or equal to the specified minimum. Used to evaluate length of significant
    digits in numeric strings that might contain formatting.
    """
    exception_class = ex.LengthError

    def __init__(self, max_length):
        self.max_length = max_length

    def evaluator(self):
        return lambda x: len(re.sub(r'[^\d]', '', x)) <= self.max_length

    def explain(self):
        return f'must have no more than {self.max_length} digit characters'


class OnlyNumbers(Rule):
    exception_class = ex.DataError  # TODO: character error

    def evaluator(self):
        return lambda x: re.fullmatch(r'\d+', x)

    def explain(self):
        return 'must only contain characters 0-9'


class NoLeadingZero(Rule):
    """
    Ensure that there is no leading zero after removing all non-digit characters.
    A lone zero (0) will not raise an error.
    """
    exception_class = ex.LeadingZeroError

    def evaluator(self):
        return lambda x: re.fullmatch(r'(0|([1-9]\d*))', re.sub(r'[^\d]', '', x))

    def explain(self):
        return 'cannot have a leading zero digit'


class CanBeFloat(Rule):
    exception_class = ex.ConversionError

    def evaluator(self):
        return lambda x: isinstance(float(x), float)

    def explain(self):
        return 'can be coerced into a float value'


class CanBeInteger(Rule):
    exception_class = ex.ConversionError

    def evaluator(self):
        return lambda x: isinstance(int(x), int)

    def explain(self):
        return 'can be coerced into an integer value'


class CanBeDateIso(Rule):
    exception_class = ex.ConversionError

    def evaluator(self):
        return lambda x: isinstance(datetime.strptime(x, '%Y-%m-%d'), datetime)

    def explain(self):
        return 'can be coerced into a ISO-8601 date'


class NumericDecimals(Rule):
    exception_class = ex.CurrencyPatternError

    def __init__(self, decimals=2):
        self.decimals = decimals

    def evaluator(self):
        return lambda x: re.fullmatch(r'-?\d+(\.\d{1,2})?', x)

    def explain(self):
        return f'cannot have more than {self.decimals} digits after the decimal point'


class LengthComparison(Rule):
    """
    Base float value comparison class. Requires that the value can be coerced
    to a float value.
    """
    exception_class = ex.ValueComparisonError
    comparison_language = 'N/A'

    def __init__(self, comparison_value):
        self.comparison_value = comparison_value

    def explain(self) -> str:
        return f'{self.comparison_language} {str(self.comparison_value)}'


class LengthGT(LengthComparison):
    """ Length Greater Than comparison """
    comparison_language = 'greater than'

    def evaluator(self):
        return lambda x: len(x) > self.comparison_value


class LengthGTE(LengthComparison):
    """ Length Greater Than or Equal To comparison """
    comparison_language = 'greater than or equal to'

    def evaluator(self):
        return lambda x: len(x) >= self.comparison_value


class LengthET(LengthComparison):
    """ Length Equal To comparison """
    comparison_language = 'equal to'

    def evaluator(self):
        return lambda x: len(x) == self.comparison_value


class LengthLTE(LengthComparison):
    """ Length Less Than or Equal To comparison """
    comparison_language = 'less than or equal to'

    def evaluator(self):
        return lambda x: len(x) <= self.comparison_value


class LengthLT(LengthComparison):
    """ Length Less Than comparison """
    comparison_language = 'less than'

    def evaluator(self):
        return lambda x: len(x) < self.comparison_value


class NumericComparison(Rule):
    """
    Base float value comparison class. Requires that the value can be coerced
    to a float value.
    """
    exception_class = ex.ValueComparisonError
    comparison_language = 'N/A'

    def __init__(self, comparison_value):
        self.comparison_value = comparison_value

    def explain(self) -> str:
        return f'{self.comparison_language} {str(self.comparison_value)}'


class NumericGT(NumericComparison):
    """ Numeric Greater Than comparison """
    comparison_language = 'greater than'

    def evaluator(self):
        return lambda x: float(x) > self.comparison_value


class NumericGTE(NumericComparison):
    """ Numeric Greater Than or Equal To comparison """
    comparison_language = 'greater than or equal to'

    def evaluator(self):
        return lambda x: float(x) >= self.comparison_value


class NumericET(NumericComparison):
    """ Numeric Equal To comparison """
    comparison_language = 'equal to'

    def evaluator(self):
        return lambda x: float(x) == self.comparison_value


class NumericLTE(NumericComparison):
    """ Numeric Less Than or Equal To comparison """
    comparison_language = 'less than or equal to'

    def evaluator(self):
        return lambda x: float(x) <= self.comparison_value


class NumericLT(NumericComparison):
    """ Numeric Less Than comparison """
    comparison_language = 'less than'

    def evaluator(self):
        return lambda x: float(x) < self.comparison_value


class DateComparison(Rule):
    """
    Base date value comparison class. Requires that the value can be coerced
    to a date using the specified format for the field.
    """
    exception_class = ex.ValueComparisonError
    comparison_language = 'N/A'

    def __init__(self, comparison_value, date_format='%Y%m%d'):
        self.date_format = date_format
        self.comparison_value = datetime.strptime(comparison_value, date_format)

    def explain(self) -> str:
        return f'{self.comparison_language} {str(self.comparison_value)}'


class DateGT(DateComparison):
    """ Date Greater Than comparison """
    comparison_language = 'greater than'

    def evaluator(self):
        return lambda x: datetime.strptime(x, self.date_format) > self.comparison_value


class DateGTE(DateComparison):
    """ Date Greater Than or Equal To comparison """
    comparison_language = 'greater than or equal to'

    def evaluator(self):
        return lambda x: datetime.strptime(x, self.date_format) >= self.comparison_value


class DateET(DateComparison):
    """ Date Equal To comparison """
    comparison_language = 'equal to'

    def evaluator(self):
        return lambda x: datetime.strptime(x, self.date_format) == self.comparison_value


class DateLTE(DateComparison):
    """ Date Less Than or Equal To comparison """
    comparison_language = 'less than or equal to'

    def evaluator(self):
        return lambda x: datetime.strptime(x, self.date_format) <= self.comparison_value


class DateLT(DateComparison):
    """ Date Less Than comparison """
    comparison_language = 'less than'

    def evaluator(self):
        return lambda x: datetime.strptime(x, self.date_format) < self.comparison_value


class RowLengthLTE(Rule):
    exception_class = ex.RowLengthError

    def __init__(self, comparison_value):
        self.comparison_value = comparison_value

    def evaluator(self):
        return lambda x: len(x) <= self.comparison_value

    def explain(self) -> str:
        return f'row length must be equal to {str(self.comparison_value)}, not greater'


class RowLengthGTE(Rule):
    exception_class = ex.RowLengthError

    def __init__(self, comparison_value):
        self.comparison_value = comparison_value

    def evaluator(self):
        return lambda x: len(x) >= self.comparison_value

    def explain(self) -> str:
        return f'row length must be equal to {str(self.comparison_value)}, not less'


class HeaderRule(Rule):
    def __init__(self, definition):
        self.definition = definition


class HeaderColumnOrder(HeaderRule):
    exception_class = ex.DataError

    def evaluator(self):
        return lambda x: x == list(self.definition)

    def explain(self):
        return 'Header row must explicitly match order of definition'


class HeaderNoExtra(HeaderRule):
    exception_class = ex.UnexpectedColumnError

    def evaluator(self):
        return lambda x: all([y in self.definition for y in x])

    def explain(self):
        return 'Header row must not have unexpected columns'


class HeaderNoMissing(HeaderRule):
    exception_class = ex.MissingColumnError

    def evaluator(self):
        return lambda x: all([y in x for y in self.definition])

    def explain(self) -> str:
        return 'Header row must not be missing any expected columns'


class HeaderNoDuplicate(HeaderRule):
    exception_class = ex.DuplicateColumnError

    def evaluator(self):
        return lambda x: len(x) == len(set(x))

    def explain(self):
        return 'Header row must not contain duplicate values'


class FileRule(Rule):
    pass


class FileExists(FileRule):
    exception_class = FileNotFoundError

    def evaluator(self):
        return lambda x: Path(x).exists()

    def explain(self) -> str:
        return 'file must exist'


class FileNameMatchesPattern(FileRule):
    exception_class = ex.FilePatternError

    def __init__(self, pattern: Union[re.Pattern, List[re.Pattern]]):
        self.patterns = [pattern] if isinstance(pattern, re.Pattern) else pattern

    def evaluator(self):
        return lambda x: any([p.fullmatch(Path(x).name) for p in self.patterns])

    def explain(self) -> str:
        return 'file name must match a pattern provided in the layout'


class FileNameMatchesOnePattern(FileRule):
    exception_class = ex.UrNotMyDataError

    def __init__(self, patterns: list):
        self.patterns = patterns

    def evaluator(self):
        return lambda x: sum([
            True if p.fullmatch(Path(x).name) else False for p in self.patterns
        ]) <= 1

    def explain(self) -> str:
        return 'file cannot match multiple patterns provided in the layout'
