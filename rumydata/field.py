"""
rumydata field/column/element objects

This submodule contains the various field type objects that are used to define
the fields (i.e. columns, elements) that make up a tabular data set. These field
objects can be extended by adding additional rules in the rules keyword of the
fields constructor. Additional modification, including the definition of
entirely new field types can be achieved by subclassing the Field base class.

See the rumydata.rules submodule to learn more about the use of rules to extend
field class behavior.
"""
from typing import Union, Tuple, Dict, List

from rumydata import exception as ex
from rumydata.base import BaseSubject
from rumydata.rules import cell as clr, column as cr

__all__ = ['Text', 'Date', 'Currency', 'Digit', 'Integer', 'Choice']


class Field(BaseSubject):
    """
    Base Field class

    This class provides the framework for the definition of field types in this
    package.
    """

    def __init__(self, nullable=False, rules: list = None):
        """
        Base Field constructor

        :param nullable: a boolean indicator which controls whether the field
            can be null (blank). Defaults to False, which will cause errors to
            be raised when checking empty strings.
        :param rules: a list of rules to apply to this field during checks.
        """

        super().__init__(rules)
        self.nullable = nullable

        if not self.nullable:
            self.rules.append(clr.NotNull())

    def __check__(self, data, cix=-1, rule_type=None, **kwargs) -> Union[ex.CellError, None]:
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
        if self.nullable and issubclass(rule_type, clr.Rule) and data == '':
            pass
        else:
            e = super().__check__(data, rule_type=rule_type)
            if e:
                return ex.CellError(cix, errors=e, **kwargs)

    def check_cell(self, value: Union[str, Tuple[str, Dict]], **kwargs):
        """
        Cell Rule assertion

        Perform an assertion of the provided cell value against the rules
        defined for the field. If the value fails the check for any of the
        rules, the assertion will raise a detailed exception message.

        :param value: a cell value, either a string or a tuple of a string
            and a dictionary, to be checked.
        """

        errors = self.__check__(value, rule_type=clr.Rule, **kwargs)
        assert not errors, str(errors)

    def check_column(self, values: List[str], **kwargs):
        """
        Column Rule assertion

        Perform an assertion of the provided column values against the rules
        defined for the field. If the values fail the check for any of the
        rules, the assertion will raise a detailed exception message.

        :param values: a list of values contained in the column.
        """

        errors = self.__check__(values, rule_type=cr.Rule, **kwargs)
        assert not errors, str(errors)

    def digest(self):
        dig = super().digest()
        if self.nullable:
            dig.append('Nullable')
        return dig

    def comparison_columns(self) -> set:
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

    def __has_rule_type__(self, rule_type):
        return any([issubclass(type(r), rule_type) for r in self.rules])


class Ignore(Field):
    """
    Ignore the values found in this field. This will cause other dependencies
    (like row checks) to treat any values in this field as if they were empty.
    While the check method still exists, this class overwrites those inherited
    methods to intentionally have no effect.
    """

    # noinspection PyMissingConstructor
    def __init__(self):
        self.rules = []
        self.descriptors = {}

    def __check__(self, *args, **kwargs):
        pass


class Text(Field):
    def __init__(self, max_length, min_length=None, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'String'
        self.descriptors['Max Length'] = f'{str(max_length)} characters'

        self.rules.append(clr.MaxChar(max_length))

        if min_length:
            self.descriptors['Min Length'] = f'{str(min_length)} characters'
            self.rules.append(clr.MinChar(min_length))


class Date(Field):
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
    def __init__(self, significant_digits: int, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Numeric'
        self.descriptors['Format'] = f'{"9" * (significant_digits - 2)}.99'
        self.descriptors['Max Length'] = f'{str(significant_digits)} digits'

        self.rules.append(clr.MaxDigit(significant_digits))
        self.rules.append(clr.NumericDecimals())


class Digit(Field):
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
    def __init__(self, valid_values: list, case_insensitive=False, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Choice'
        self.descriptors['Choices'] = ','.join(valid_values)
        self.rules.append(
            clr.Choice(valid_values, case_insensitive=case_insensitive)
        )
