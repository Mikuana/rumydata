from typing import Union, Tuple, AnyStr, Dict

from rumydata import exception as ex
from rumydata.base import BaseSubject
from rumydata.rules import cell as clr, column as cr

__all__ = [
    'Field', 'Text', 'Date', 'Currency', 'Digit', 'Integer', 'Choice'
]


class Field(BaseSubject):
    def __init__(self, nullable=False, rules: list = None):
        super().__init__(rules)
        self.nullable = nullable

        if not self.nullable:
            self.rules.append(clr.NotNull())

    def __check__(self, data, cix=-1, rule_type=None, **kwargs):
        # if data is nullable and value is empty, skip all checks
        if self.nullable and issubclass(rule_type, clr.Rule) and data == '':
            pass
        else:
            e = super().__check__(data, rule_type=rule_type)
            if e:
                return ex.CellError(cix, errors=e, **kwargs)

    def check_cell(self, value: Union[AnyStr, Tuple[AnyStr, Dict]], **kwargs):
        errors = self.__check__(value, rule_type=clr.Rule, **kwargs)
        assert not errors, str(errors)

    def check_column(self, values: list, **kwargs):
        errors = self.__check__(values, rule_type=cr.Rule, **kwargs)
        assert not errors, str(errors)

    def digest(self):
        dig = super().digest()
        if self.nullable:
            dig.append('Nullable')
        return dig

    def comparison_columns(self):
        compares = set()
        for r in self.rules:
            if issubclass(type(r), clr.ColumnComparisonRule):
                compares.add(r.compare_to)
        return compares

    def has_rule_type(self, rule_type):
        return any([issubclass(type(r), rule_type) for r in self.rules])


class Ignore(Field):
    """
    Ignore the values found in this field. This will cause other dependencies (like row checks) to
    treat any values in this field as if they were empty. While the check method still exists, this
    class overwrites those inherited methods to intentionally have no effect.
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
