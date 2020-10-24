"""
field/column/element objects

This submodule contains the various field type objects that are used to define
the fields (i.e. columns, elements) that make up a tabular data set. These field
objects can be extended by adding additional rules in the rules keyword of the
fields constructor. Additional modification, including the definition of
entirely new field types can be achieved by subclassing the Field base class.

All field subclasses pass their keyword arguments to the base Field class. See
documentation for the base Field for a complete listing of optional keyword
arguments, including rules extension.

See the rumydata.rules submodule to learn more about the use of rules to extend
field class behavior.
"""
from typing import Union, Tuple, Dict, List

from rumydata import exception as ex
from rumydata._base import _BaseSubject
from rumydata.rules import cell as clr, column as cr

__all__ = ['Text', 'Date', 'Currency', 'Digit', 'Integer', 'Choice', 'Ignore']


class Field(_BaseSubject):
    """
    Base Field class

    This class provides the framework for the definition of field types in this
    package.

    :param nullable: a boolean indicator which controls whether the field
        can be null (blank). Defaults to False, which will cause errors to
        be raised when checking empty strings.
    :param rules: a list of rules to apply to this field during checks.
    :param strip: (optional) apply pre-processing to values in the field which
        applies the str.strip method, removing leading and trailing whitespaces,
        prior to checking rules.
    """

    def __init__(self, nullable=False, rules: list = None, **kwargs):
        super().__init__(rules)
        self.nullable = nullable
        self.strip = kwargs.get('strip')

        if not self.nullable:
            self.rules.append(clr.NotNull())

    def check_cell(self, value: Union[str, Tuple[str, Dict]], **kwargs):
        """
        Cell Rule assertion

        Perform an assertion of the provided cell value against the rules
        defined for the field. If the value fails the check for any of the
        rules, the assertion will raise a detailed exception message.

        :param value: a cell value, either a string or a tuple of a string
            and a dictionary, to be checked.
        """

        errors = self._check(value, rule_type=clr.Rule, **kwargs)
        assert not errors, str(errors)

    def check_column(self, values: List[str], **kwargs):
        """
        Column Rule assertion

        Perform an assertion of the provided column values against the rules
        defined for the field. If the values fail the check for any of the
        rules, the assertion will raise a detailed exception message.

        :param values: a list of values contained in the column.
        """

        errors = self._check(values, rule_type=cr.Rule, **kwargs)
        assert not errors, str(errors)

    def _check(self, data, cix=-1, rule_type=None, **kwargs) -> Union[ex.CellError, ex.ColumnError, None]:
        """
        Check data against field rules of specified rule type

        This is the core method used to evaluate data against a subject defined
        by this class.

        :param data: an object which conforms to the `prepare` method of the
            class specified in the rule_type parameter
        :param cix: column index used for error reporting.
        :param rule_type: a Rule class belonging to one of the submodules in the
            rules module (e.g. rumydata.rules.cell.Rule). This controls the
            types of rules that the provided data will be checked against.
        :return: a list of any errors that were raised while checking the data.
        """

        # if data is nullable and value is empty, skip all checks
        empty = data[0] == '' if isinstance(data, tuple) else data == ''
        if self.nullable and rule_type == clr.Rule and empty:
            pass
        else:
            e = super()._check(data, rule_type=rule_type, strip=self.strip)
            if e:
                if rule_type == cr.Rule:
                    return ex.ColumnError(cix, errors=e, **kwargs)
                else:
                    return ex.CellError(cix, errors=e, **kwargs)

    def _comparison_columns(self) -> set:
        """
        Comparison fields report

        A method to report the columns that will need to be compared while
        checking rules.

        :return: a set of the columns that will need to be compared.
        """
        compares = set()
        for r in self.rules:
            if issubclass(type(r), clr.ColumnComparisonRule):
                compares.add(r.compare_to)
        return compares

    def _has_rule_type(self, rule_type):
        return any([issubclass(type(r), rule_type) for r in self.rules])

    def _digest(self):
        dig = super()._digest()
        if self.nullable:
            dig.append('Nullable')
        return dig


class Ignore(Field):
    """
    Ignore the values found in this field. This will cause other dependencies
    (like row checks) to treat any values in this field as if they were empty.
    While the check method still exists, this class overwrites those inherited
    methods to intentionally have no effect.
    """

    # noinspection PyMissingConstructor
    def __init__(self):
        self.nullable = True
        self.rules = []
        self.descriptors = {}

    def _check(self, *args, **kwargs):
        pass


class Text(Field):
    """
    Text Field

    A field made up entirely of text. This is one of the least restrictive field
    types, enforcing only a maximum and (optional) minimum length.

    :param max_length: the maximum number of allowable characters
    :param min_length: (optional) the minimum number of allowable characters
    """

    _default_args = (1,)

    def __init__(self, max_length, min_length=None, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'String'
        self.descriptors['Max Length'] = f'{str(max_length)} characters'

        self.rules.append(clr.MaxChar(max_length))

        if min_length:
            self.descriptors['Min Length'] = f'{str(min_length)} characters'
            self.rules.append(clr.MinChar(min_length))


class Date(Field):
    """
    Date field

    A date value formatted in ISO-8601 (YYYY-MM-DD). Rules can be applied to
    restrict minimum and maximum date. If your date string includes, or might
    include an empty timestamp (00:00:00), the truncate_time parameter can be
    used to remove this empty timestamp prior to validation, preventing it from
    causing failure.

    :param min_date: the minimum date value allowed
    :param max_date: the maximum date value allowed
    """

    def __init__(self, min_date: str = None, max_date: str = None, **kwargs):
        rule_kwargs = {
            'truncate_time': kwargs.pop('truncate_time', False)
        }
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Date'
        self.descriptors['Format'] = 'YYYY-MM-DD'

        self.rules.append(clr.CanBeDateIso(**rule_kwargs))

        if max_date:
            self.descriptors['Max Date'] = f'{max_date}'
            self.rules.append(clr.DateLTE(max_date, **rule_kwargs))

        if min_date:
            self.descriptors['Min Date'] = f'{min_date}'
            self.rules.append(clr.DateGTE(min_date, **rule_kwargs))


class Currency(Field):
    """
    Currency field

    A numeric field which represents a currency value. Defaults to a maximum
    of two decimal points.

    :param significant_digits: an integer which specifies the maximum number of
        decimals that are allowed in the value.
    """

    _default_args = (5,)

    def __init__(self, significant_digits: int, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Numeric'
        self.descriptors['Format'] = f'{"9" * (significant_digits - 2)}.99'
        self.descriptors['Max Length'] = f'{str(significant_digits)} digits'

        self.rules.append(clr.MaxDigit(significant_digits))
        self.rules.append(clr.NumericDecimals())


class Digit(Field):
    """
    Digit field

    A value made up entirely of digits (numbers). The main difference between
    this field and an Integer, is that this field will allow leading zeroes
    (e.g 0123), while an Integer would not.

    :param max_length: the maximum number of digits
    :param min_length: (optional) the minimum number of digits
    """

    _default_args = (1,)

    def __init__(self, max_length, min_length=None, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Numeric'
        self.descriptors['Format'] = f'{"0" * max_length}'
        self.descriptors['Max Length'] = f'{str(max_length)} digits'

        self.rules.append(clr.OnlyNumbers())
        self.rules.append(clr.MaxChar(max_length))

        if min_length:
            self.descriptors['Min Length'] = f'{str(min_length)} digits'
            self.rules.append(clr.MinChar(min_length))


class Integer(Field):
    """
    Integer field

    A value made up entirely of digits (numbers). A whole number.

    :param max_length: the maximum number of digits
    :param min_length: (optional) the minimum number of digits
    """

    _default_args = (1,)

    def __init__(self, max_length, min_length=None, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Numeric'
        self.descriptors['Format'] = f'{"9" * max_length}'
        self.descriptors['Max Length'] = f'{str(max_length)} digits'

        self.rules.append(clr.CanBeInteger())
        self.rules.append(clr.NoLeadingZero())
        self.rules.append(clr.MaxDigit(max_length))

        if min_length:
            self.descriptors['Min Length'] = f'{str(max_length)} digits'
            self.rules.append(clr.MinDigit(min_length))


class Choice(Field):
    """
    Choice field

    A field with one of a pre-defined set of values.

    :param valid_values: a list of values which are considered valid
    :param case_insensitive: a boolean control which defaults to False, making
        the check of valid values case sensitive.
    """

    _default_args = (['x'],)

    def __init__(self, valid_values: list, case_insensitive=False, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Choice'
        self.descriptors['Choices'] = ','.join(valid_values)
        self.rules.append(
            clr.Choice(valid_values, case_insensitive=case_insensitive)
        )
