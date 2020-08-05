from rumydata import exception as ex
from rumydata.base import BaseSubject
from rumydata.cell import rule


class Cell(BaseSubject):
    def __init__(self, nullable=False, rules: list = None):
        super().__init__(rules)
        self.nullable = nullable

        if not self.nullable:
            self.rules.append(rule.NotNull())

    def __check__(self, data, cix=-1, **kwargs):
        # if data is nullable and value is empty, skip all checks
        if self.nullable and data.value == '':
            pass
        else:
            e = super().__check__(data, restrict=kwargs.get('restrict', rule.Rule))
            if e:
                return ex.CellError(cix, errors=e, **kwargs)

    def check(self, data, **kwargs):
        errors = self.__check__(data, **kwargs)
        assert not errors, str(errors)

    def digest(self):
        dig = super().digest()
        if self.nullable:
            dig.append('Nullable')
        return dig

    def comparison_columns(self):
        compares = set()
        for r in self.rules:
            if issubclass(type(r), rule.ColumnComparisonRule):
                compares.add(r.compare_to)
        return compares

    def has_rule_type(self, rule_type):
        return any([issubclass(type(r), rule_type) for r in self.rules])


class Text(Cell):
    def __init__(self, max_length, min_length=None, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'String'
        self.descriptors['Max Length'] = f'{str(max_length)} characters'

        self.rules.append(rule.MaxChar(max_length))

        if min_length:
            self.descriptors['Min Length'] = f'{str(min_length)} characters'
            self.rules.append(rule.MinChar(min_length))


class Date(Cell):
    def __init__(self, min_date: str = None, max_date: str = None, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Date'
        self.descriptors['Format'] = 'YYYY-MM-DD'

        self.rules.append(rule.CanBeDateIso())

        if max_date:
            self.descriptors['Max Date'] = f'{max_date}'
            self.rules.append(rule.DateLTE(max_date))

        if min_date:
            self.descriptors['Min Date'] = f'{min_date}'
            self.rules.append(rule.DateGTE(min_date))


class Currency(Cell):
    def __init__(self, significant_digits: int, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Numeric'
        self.descriptors['Format'] = f'{"9" * (significant_digits - 2)}.99'
        self.descriptors['Max Length'] = f'{str(significant_digits)} digits'

        self.rules.append(rule.MaxDigit(significant_digits))
        self.rules.append(rule.NumericDecimals())


class Digit(Cell):
    def __init__(self, max_length, min_length=None, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Numeric'
        self.descriptors['Format'] = f'{"0" * max_length}'
        self.descriptors['Max Length'] = f'{str(max_length)} digits'

        self.rules.append(rule.OnlyNumbers())
        self.rules.append(rule.MaxChar(max_length))

        if min_length:
            self.descriptors['Min Length'] = f'{str(min_length)} digits'
            self.rules.append(rule.MinChar(min_length))


class Integer(Cell):
    def __init__(self, max_length, min_length=None, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Numeric'
        self.descriptors['Format'] = f'{"9" * max_length}'
        self.descriptors['Max Length'] = f'{str(max_length)} digits'

        self.rules.append(rule.CanBeInteger())
        self.rules.append(rule.NoLeadingZero())
        self.rules.append(rule.MaxDigit(max_length))

        if min_length:
            self.descriptors['Min Length'] = f'{str(max_length)} digits'
            self.rules.append(rule.MinDigit(min_length))


class Choice(Cell):
    def __init__(self, valid_values: list, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Choice'
        self.descriptors['Choices'] = ','.join(valid_values)
        self.rules.append(rule.Choice(valid_values))
