import re
from datetime import datetime
from typing import Union, Tuple, Dict, AnyStr, List

from rumydata import exception as ex
from rumydata.base import BaseRule


class Rule(BaseRule):

    def prepare(self, data: Union[AnyStr, Tuple[AnyStr, Dict]]) -> tuple:
        if isinstance(data, str):
            return data,
        else:
            return data[0],


class NotNull(Rule):
    exception_class = ex.NullValueError

    def evaluator(self):
        return lambda x: x != ''

    def exception_msg(self):
        return self.exception_class(self.explain())

    def explain(self):
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

    def __init__(self, choices: List[str], case_insensitive=False):
        self.choices = choices
        self.case_insensitive = case_insensitive
        self.eval_choices = [x.lower() for x in choices] if case_insensitive else choices

    def prepare(self, data: str) -> tuple:
        if self.case_insensitive:
            return data.lower(),
        else:
            return data,

    def evaluator(self):
        return lambda x: x in self.eval_choices

    def explain(self):
        return (
            f'must be one of {self.choices}'
            f'{" (case insensitive)" if self.case_insensitive else " (case sensitive)"}'
        )


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
    exception_class = ex.CharacterError

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


class DateRule(Rule):
    exception_class = ex.ConversionError

    def __init__(self, **kwargs):
        self.truncate_time = kwargs.pop('truncate_time', False)
        super().__init__(**kwargs)

    def prepare(self, data: Union[str, Tuple[str, Dict]]) -> tuple:
        if self.truncate_time:
            no_time = ' 00:00:00'
            if isinstance(data, str) and data.endswith(no_time):
                data = data[:-len(no_time)]
            elif data[0].endswith(no_time):
                data = data[0][:-len(no_time)], data[1]

        return super().prepare(data)


class CanBeDateIso(DateRule):
    def evaluator(self):
        return lambda x: isinstance(datetime.strptime(x, '%Y-%m-%d'), datetime)

    def explain(self):
        return 'can be coerced into a ISO-8601 date'


class DateComparison(DateRule):
    """
    Base date value comparison class. Requires that the value can be coerced
    to a date using the specified format for the field.
    """
    exception_class = ex.ValueComparisonError
    comparison_language = 'N/A'

    def __init__(self, comparison_value, date_format='%Y-%m-%d', **kwargs):
        self.date_format = date_format
        self.comparison_value = datetime.strptime(comparison_value, date_format)
        super().__init__(**kwargs)

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


def make_static_cell_rule(func, assertion, exception=ex.UrNotMyDataError) -> Rule:
    """
    Return a factory generated Rule class. The function used by the rule must
    directly evaluate a single positional argument (i.e. x, but not x and y).
    Because the Rule cannot be passed a value on initialization, neither the
    evaluator or explain methods in the return class can be dynamic.
    """

    class FactoryRule(Rule):
        exception_class = exception

        def evaluator(self):
            return func

        def explain(self) -> str:
            return assertion

    return FactoryRule()


class ColumnComparisonRule(Rule):
    exception_class = ex.ColumnComparisonError

    def __init__(self, compare_to: str):
        self.compare_to = compare_to

    def prepare(self, data: Tuple[AnyStr, Dict]) -> tuple:
        return data[0], data[1][self.compare_to]


class GreaterThanColumn(ColumnComparisonRule):
    def evaluator(self):
        return lambda x, y: x > y

    def explain(self) -> str:
        return f"must be greater than column '{self.compare_to}'"
