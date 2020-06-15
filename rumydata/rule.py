import re
from datetime import datetime

from rumydata import exception as ex


class Rule:
    """ Base class for defining data type rules """

    def evaluator(self):
        """
        :return: a function which expects to evaluate to True, if the value
        provided to the function meets the rule.
        """
        pass

    def exception(self):
        """
        :return: a sanitized error message which is specific to the function,
        contains no direct link to the value that was checked.
        """
        pass


class Nullable(Rule):
    @classmethod
    def evaluator(cls):
        return lambda x: x != ''

    @classmethod
    def exception(cls):
        return ex.NullValueError('value is empty/blank')


class ExactChar(Rule):
    def __init__(self, exact_length):
        self.exact_length = exact_length

    def evaluator(self):
        return lambda x: len(x) == self.exact_length

    def exception(self):
        return ex.DataLengthError(
            f'value is not exactly {str(self.exact_length)} characters'
        )


class MinChar(Rule):
    def __init__(self, min_length):
        self.min_length = min_length

    def evaluator(self):
        return lambda x: len(x) >= self.min_length

    def exception(self):
        return ex.DataLengthError(
            f'value exceeds max characters ({str(self.min_length)})'
        )


class MaxChar(Rule):
    def __init__(self, max_length):
        self.max_length = max_length

    def evaluator(self):
        return lambda x: len(x) <= self.max_length

    def exception(self):
        return ex.DataLengthError(
            f'value exceeds max characters ({str(self.max_length)})'
        )


class Choice(Rule):
    def __init__(self, choices: list):
        self.choices = choices

    def evaluator(self):
        return lambda x: x in self.choices

    def exception(self):
        return ex.InvalidChoiceError(
            f'value not one of choices{self.choices})'
        )


class MinDigit(Rule):
    """
    Check that count of characters, after removing all non-digits, meets or
    exceeds the specified minimum. Used to evaluate length of significant digits
    in numeric strings that might contain formatting.
    """

    def __init__(self, min_length):
        self.min_length = min_length

    def evaluator(self):
        return lambda x: len(re.sub(r'[^\d]', '', x)) >= self.min_length

    def exception(self):
        return ex.DataLengthError(
            f'value exceeds max characters ({str(self.min_length)})'
        )


class MaxDigit(Rule):
    """
    Check that count of characters, after removing all non-digits, is less than
    or equal to the specified minimum. Used to evaluate length of significant
    digits in numeric strings that might contain formatting.
    """

    def __init__(self, max_length):
        self.max_length = max_length

    def evaluator(self):
        return lambda x: len(re.sub(r'[^\d]', '', x)) <= self.max_length

    def exception(self):
        return ex.DataLengthError(
            f'value exceeds max characters ({str(self.max_length)})'
        )


class OnlyNumbers(Rule):
    def evaluator(self):
        return lambda x: re.fullmatch(r'\d+', x)

    def exception(self):
        return ex.DataError('value is not made exclusively of numbers')


class NoLeadingZero(Rule):
    """
    Ensure that there is no leading zero after removing all non-digit characters.
    A lone zero (0) will not raise an error.
    """

    def evaluator(self):
        return lambda x: re.fullmatch(r'(0|([1-9]\d*))', re.sub(r'[^\d]', '', x))

    def exception(self):
        return ex.LeadingZeroError('value does not start with non-zero digit')


class CanBeFloat(Rule):
    def evaluator(self):
        return lambda x: isinstance(float(x), float)

    def exception(self):
        return ex.ConversionError('value cannot be coerced into a float type')


class CanBeInteger(Rule):
    def evaluator(self):
        return lambda x: isinstance(int(x), int)

    def exception(self):
        return ex.ConversionError('value cannot be coerced into a integer type')


class CanBeDateIso(Rule):
    def evaluator(self):
        return lambda x: isinstance(datetime.strptime(x, '%Y-%m-%d'), datetime)

    def exception(self):
        return ex.ConversionError('value cannot be coerced into a date type')


class NumericDecimals(Rule):
    def __init__(self, decimals=2):
        self.decimals = decimals

    def evaluator(self):
        return lambda x: re.fullmatch(r'-?\d+(\.\d{1,2})?', x)

    def exception(self):
        return ex.CurrencyPatternError(
            f'value exceeds the decimal limit of {str(self.decimals)}'
        )


class LengthComparison(Rule):
    """
    Base float value comparison class. Requires that the value can be coerced
    to a float value.
    """
    comparison_language = 'N/A'

    def __init__(self, comparison_value):
        self.comparison_value = comparison_value

    def description(self):
        return f'{self.comparison_language} {str(self.comparison_value)}'

    def exception(self):
        return ex.ValueComparisonError(
            f'length is not {self.comparison_language} {self.comparison_value}'
        )


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
    comparison_language = 'N/A'

    def __init__(self, comparison_value):
        self.comparison_value = comparison_value

    def description(self):
        return f'{self.comparison_language} {str(self.comparison_value)}'

    def exception(self):
        return ex.ValueComparisonError(
            f'value is not {self.comparison_language} {self.comparison_value}'
        )


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
    comparison_language = 'N/A'

    def __init__(self, comparison_value, date_format='%Y%m%d'):
        self.date_format = date_format
        self.comparison_value = datetime.strptime(comparison_value, date_format)

    def description(self):
        return f'{self.comparison_language} {str(self.comparison_value)}'

    def exception(self):
        return ex.ValueComparisonError(
            f'date is not {self.comparison_language} {self.comparison_value}'
        )


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


class HeaderRule(Rule):
    def __init__(self, definition):
        self.definition = definition


class HeaderColumnOrder(HeaderRule):

    def evaluator(self):
        return lambda x: x == list(self.definition)

    def exception(self):
        return ex.DataError('Header row may be out of expected order')


class HeaderNoExtra(HeaderRule):
    def evaluator(self):
        return lambda x: all([y in self.definition for y in x])

    def exception(self):
        return ex.UnexpectedColumnError('Header row includes an unexpected column')


class HeaderNoMissing(HeaderRule):
    def evaluator(self):
        return lambda x: all([y in x for y in self.definition])

    def exception(self):
        return ex.MissingColumnError('Header row missing an expected column')


class HeaderNoDuplicate(HeaderRule):
    def evaluator(self):
        return lambda x: len(x) == len(set(x))

    def exception(self):
        return ex.DuplicateColumnError('Header row contains duplicate value')
