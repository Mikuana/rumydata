"""
cell validation rules

These rules make up the heart of what most users of the rumydata package will
be interested in when attempting to extend the out-of-the box behavior. These
rules are generally applied to a single value, in the case of the Rule class,
but can also be used to compare the value in a cell to another value in the same
row, in the case of the ColumnComparisonRule class.

These rules are intended to be used by adding them directly to rules argument in
the constructor of the classes in the field submodule.
"""
import re
from datetime import datetime
from typing import Union, Tuple, Dict, List

from rumydata import exception as ex
from rumydata.base import BaseRule

__all__ = [
    'NotNull', 'ExactChar', 'MinChar', 'MaxChar', 'AsciiChar', 'Choice',
    'MinDigit', 'MaxDigit', 'OnlyNumbers', 'NoLeadingZero', 'CanBeFloat',
    'CanBeInteger', 'NumericDecimals', 'LengthComparison', 'LengthGT',
    'LengthGTE', 'LengthET', 'LengthLTE', 'LengthLT', 'NumericComparison',
    'NumericGT', 'NumericGTE', 'NumericET', 'NumericLTE', 'NumericLT',
    'DateRule', 'CanBeDateIso', 'DateComparison', 'DateGT', 'DateGTE', 'DateET',
    'DateLTE', 'DateLT', 'ColumnComparisonRule', 'GreaterThanColumn',
    'make_static_cell_rule'
]


class Rule(BaseRule):
    """ Cell Rule """

    def _prepare(self, data: Union[str, Tuple[str, Dict]]) -> tuple:
        if isinstance(data, str):
            return data,
        else:
            return data[0],


def make_static_cell_rule(func, assertion, exception=ex.UrNotMyDataError) -> Rule:
    """
    Static cell rule factory

    Return a factory generated Rule class. The function used by the rule must
    directly evaluate a single positional argument (i.e. x, but not x and y).
    Because the Rule cannot be passed a value on initialization, neither the
    evaluator or explain methods in the return class can be dynamic.

    :param func: a function which takes a single positional argument
    :param assertion: a string describing the condition which must be met in
        order for the function to return True
    :param exception: the UrNotMyDataError type exception to return if the
        function assertion returns false.
    :return: a rumydata.rules.cell.Rule
    """

    class FactoryRule(Rule):
        exception_class = exception

        def _evaluator(self):
            return func

        def _explain(self) -> str:
            return assertion

    return FactoryRule()


class NotNull(Rule):
    """ Cell not null Rule """

    exception_class = ex.NullValueError

    def _evaluator(self):
        return lambda x: x != ''

    def _exception_msg(self):
        return self.exception_class(self._explain())

    def _explain(self):
        return 'cannot be empty/blank'


class ExactChar(Rule):
    """ Cell exact character length Rule """

    exception_class = ex.LengthError

    def __init__(self, exact_length):
        self.exact_length = exact_length

    def _evaluator(self):
        return lambda x: len(x) == self.exact_length

    def _explain(self):
        return f'must be exactly {str(self.exact_length)} characters'


class MinChar(Rule):
    """ Cell minimum character length Rule """

    exception_class = ex.LengthError

    def __init__(self, min_length):
        self.min_length = min_length

    def _evaluator(self):
        return lambda x: len(x) >= self.min_length

    def _explain(self):
        return f'must be at least {str(self.min_length)} characters'


class MaxChar(Rule):
    """ Cell maximum character length Rule """

    exception_class = ex.LengthError

    def __init__(self, max_length):
        self.max_length = max_length

    def _evaluator(self):
        return lambda x: len(x) <= self.max_length

    def _explain(self):
        return f'must be no more than {str(self.max_length)} characters'


class AsciiChar(Rule):
    """ Cell contains only ASCII character Rule """

    exception_class = ex.UrNotMyDataError

    def _evaluator(self):
        return lambda x: all(ord(c) < 128 for c in x)

    def _explain(self) -> str:
        return 'must have only ASCII characters'


class Choice(Rule):
    """ Cell choice Rule """

    exception_class = ex.InvalidChoiceError

    def __init__(self, choices: List[str], case_insensitive=False):
        self.choices = choices
        self.case_insensitive = case_insensitive
        self.eval_choices = [x.lower() for x in choices] if case_insensitive else choices

    def _prepare(self, data: Union[str, Tuple[str, Dict]]) -> tuple:
        if self.case_insensitive:
            if isinstance(data, str):
                data = data.lower(),
            else:
                data = data[0].lower(), data[1]

        return super()._prepare(data)

    def _evaluator(self):
        return lambda x: x in self.eval_choices

    def _explain(self):
        return (
            f'must be one of {self.choices}'
            f'{" (case insensitive)" if self.case_insensitive else " (case sensitive)"}'
        )


class MinDigit(Rule):
    """
    Cell minimum digit character Rule

    Check that count of characters, after removing all non-digits, meets or
    exceeds the specified minimum. Used to evaluate length of significant digits
    in numeric strings that might contain formatting.
    """
    exception_class = ex.LengthError

    def __init__(self, min_length):
        self.min_length = min_length

    def _evaluator(self):
        return lambda x: len(re.sub(r'[^\d]', '', x)) >= self.min_length

    def _explain(self):
        return f'must have at least {str(self.min_length)} digit characters'


class MaxDigit(Rule):
    """
    Cell maximum digit character Rule

    Check that count of characters, after removing all non-digits, is less than
    or equal to the specified minimum. Used to evaluate length of significant
    digits in numeric strings that might contain formatting.
    """
    exception_class = ex.LengthError

    def __init__(self, max_length):
        self.max_length = max_length

    def _evaluator(self):
        return lambda x: len(re.sub(r'[^\d]', '', x)) <= self.max_length

    def _explain(self):
        return f'must have no more than {self.max_length} digit characters'


class OnlyNumbers(Rule):
    """ Cell only digit characters Rule """

    exception_class = ex.CharacterError

    def _evaluator(self):
        return lambda x: re.fullmatch(r'\d+', x)

    def _explain(self):
        return 'must only contain characters 0-9'


class NoLeadingZero(Rule):
    """
    Cell no leading zero digit Rule

    Ensure that there is no leading zero after removing all non-digit characters.
    A lone zero (0) will not raise an error.
    """

    exception_class = ex.LeadingZeroError

    def _evaluator(self):
        return lambda x: re.fullmatch(r'(0|([1-9]\d*))', re.sub(r'[^\d]', '', x))

    def _explain(self):
        return 'cannot have a leading zero digit'


class CanBeFloat(Rule):
    """ Cell can be float Rule """

    exception_class = ex.ConversionError

    def _evaluator(self):
        return lambda x: isinstance(float(x), float)

    def _explain(self):
        return 'can be coerced into a float value'


class CanBeInteger(Rule):
    """ Cell can be integer Rule """

    exception_class = ex.ConversionError

    def _evaluator(self):
        return lambda x: isinstance(int(x), int)

    def _explain(self):
        return 'can be coerced into an integer value'


class NumericDecimals(Rule):
    """ Cell has maximum decimals Rule """

    exception_class = ex.CurrencyPatternError

    def __init__(self, decimals=2):
        self.decimals = decimals

    def _evaluator(self):
        return lambda x: re.fullmatch(r'-?\d+(\.\d{1,2})?', x)

    def _explain(self):
        return f'cannot have more than {self.decimals} digits after the decimal point'


class LengthComparison(Rule):
    """ Base length comparison Rule """

    exception_class = ex.ValueComparisonError
    comparison_language = 'N/A'

    def __init__(self, comparison_value):
        self.comparison_value = comparison_value

    def _explain(self) -> str:
        return f'{self.comparison_language} {str(self.comparison_value)}'


class LengthGT(LengthComparison):
    """ Length greater than comparison Rule """

    comparison_language = 'greater than'

    def _evaluator(self):
        return lambda x: len(x) > self.comparison_value


class LengthGTE(LengthComparison):
    """ Length greater than or equal to comparison Rule """

    comparison_language = 'greater than or equal to'

    def _evaluator(self):
        return lambda x: len(x) >= self.comparison_value


class LengthET(LengthComparison):
    """ Length equal to comparison Rule """

    comparison_language = 'equal to'

    def _evaluator(self):
        return lambda x: len(x) == self.comparison_value


class LengthLTE(LengthComparison):
    """ Length less than or equal to comparison Rule """

    comparison_language = 'less than or equal to'

    def _evaluator(self):
        return lambda x: len(x) <= self.comparison_value


class LengthLT(LengthComparison):
    """ Length less than comparison Rule """

    comparison_language = 'less than'

    def _evaluator(self):
        return lambda x: len(x) < self.comparison_value


class NumericComparison(Rule):
    """
    Numeric length comparison base Rule

    Base float value comparison class. Requires that the value can be coerced
    to a float value.
    """

    exception_class = ex.ValueComparisonError
    comparison_language = 'N/A'

    def __init__(self, comparison_value):
        self.comparison_value = comparison_value

    def _explain(self) -> str:
        return f'{self.comparison_language} {str(self.comparison_value)}'


class NumericGT(NumericComparison):
    """ Numeric greater than comparison Rule """

    comparison_language = 'greater than'

    def _evaluator(self):
        return lambda x: float(x) > self.comparison_value


class NumericGTE(NumericComparison):
    """ Numeric greater than or equal to comparison Rule """

    comparison_language = 'greater than or equal to'

    def _evaluator(self):
        return lambda x: float(x) >= self.comparison_value


class NumericET(NumericComparison):
    """ Numeric equal to comparison Rule """

    comparison_language = 'equal to'

    def _evaluator(self):
        return lambda x: float(x) == self.comparison_value


class NumericLTE(NumericComparison):
    """ Numeric less than or equal to comparison Rule """

    comparison_language = 'less than or equal to'

    def _evaluator(self):
        return lambda x: float(x) <= self.comparison_value


class NumericLT(NumericComparison):
    """ Numeric less than comparison Rule """
    comparison_language = 'less than'

    def _evaluator(self):
        return lambda x: float(x) < self.comparison_value


class DateRule(Rule):
    """ Base date Rule """

    exception_class = ex.ConversionError

    def __init__(self, **kwargs):
        self.truncate_time = kwargs.pop('truncate_time', False)
        super().__init__(**kwargs)

    def _prepare(self, data: Union[str, Tuple[str, Dict]]) -> tuple:
        if self.truncate_time:
            no_time = ' 00:00:00'
            if isinstance(data, str) and data.endswith(no_time):
                data = data[:-len(no_time)]
            elif data[0].endswith(no_time):
                data = data[0][:-len(no_time)], data[1]

        return super()._prepare(data)


class CanBeDateIso(DateRule):
    """ Can be ISO-8601 date Rule """

    def _evaluator(self):
        return lambda x: isinstance(datetime.strptime(x, '%Y-%m-%d'), datetime)

    def _explain(self):
        return 'can be coerced into a ISO-8601 date'


class DateComparison(DateRule):
    """
    Base date comparison Rule

    Base date value comparison class. Requires that the value can be coerced
    to a date using the specified format for the field.
    """

    exception_class = ex.ValueComparisonError
    comparison_language = 'N/A'

    def __init__(self, comparison_value, date_format='%Y-%m-%d', **kwargs):
        self.date_format = date_format
        self.comparison_value = datetime.strptime(comparison_value, date_format)
        super().__init__(**kwargs)

    def _explain(self) -> str:
        return f'{self.comparison_language} {str(self.comparison_value)}'


class DateGT(DateComparison):
    """ Date greater than comparison Rule """

    comparison_language = 'greater than'

    def _evaluator(self):
        return lambda x: datetime.strptime(x, self.date_format) > self.comparison_value


class DateGTE(DateComparison):
    """ Date greater than or equal to comparison """

    comparison_language = 'greater than or equal to'

    def _evaluator(self):
        return lambda x: datetime.strptime(x, self.date_format) >= self.comparison_value


class DateET(DateComparison):
    """ Date equal to comparison Rule """

    comparison_language = 'equal to'

    def _evaluator(self):
        return lambda x: datetime.strptime(x, self.date_format) == self.comparison_value


class DateLTE(DateComparison):
    """ Date less than or equal to comparison Rule """

    comparison_language = 'less than or equal to'

    def _evaluator(self):
        return lambda x: datetime.strptime(x, self.date_format) <= self.comparison_value


class DateLT(DateComparison):
    """ Date less than comparison Rule """

    comparison_language = 'less than'

    def _evaluator(self):
        return lambda x: datetime.strptime(x, self.date_format) < self.comparison_value


class ColumnComparisonRule(Rule):
    """ Base column comparison Rule """

    exception_class = ex.ColumnComparisonError

    def __init__(self, compare_to: str):
        self.compare_to = compare_to

    def _prepare(self, data: Tuple[str, Dict]) -> tuple:
        return data[0], data[1][self.compare_to]


class GreaterThanColumn(ColumnComparisonRule):
    """ Greater than compared column Rule """

    def _evaluator(self):
        return lambda x, y: x > y

    def _explain(self) -> str:
        return f"must be greater than column '{self.compare_to}'"
