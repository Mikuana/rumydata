import csv
import re
from pathlib import Path
from typing import Union, List

from rumydata import rule
from rumydata.component import DataValidator, Layout


class Text(DataValidator):
    def __init__(self, max_length, min_length=None, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'String'
        self.descriptors['Max Length'] = f'{str(max_length)} characters'

        self.rules.append(rule.MaxChar(max_length))

        if min_length:
            self.descriptors['Min Length'] = f'{str(min_length)} characters'
            self.rules.append(rule.MinChar(min_length))


class Date(DataValidator):
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
            self.rules.append(rule.DateGTE(max_date))


class Currency(DataValidator):
    def __init__(self, significant_digits: int, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Numeric'
        self.descriptors['Format'] = f'{"9" * (significant_digits - 2)}.99'
        self.descriptors['Max Length'] = f'{str(significant_digits)} digits'

        self.rules.append(rule.MaxDigit(significant_digits))
        self.rules.append(rule.NumericDecimals())


class Digit(DataValidator):
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


class Integer(DataValidator):
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


class Choice(DataValidator):
    def __init__(self, valid_values: list, **kwargs):
        super().__init__(**kwargs)

        self.descriptors['Type'] = 'Choice'
        self.descriptors['Choices'] = ','.join(valid_values)
        self.rules.append(rule.Choice(valid_values))


class Row(DataValidator):
    def __init__(self, definition, **kwargs):
        super().__init__(**kwargs)
        expected_length = len(list(definition.keys()))

        self.rules.extend([
            rule.LengthLTE(expected_length),
            rule.LengthET(expected_length),
            rule.LengthGTE(expected_length)
        ])


class Header(DataValidator):
    def __init__(self, definition, **kwargs):
        super().__init__(**kwargs)

        self.rules.extend([
            rule.HeaderColumnOrder(definition),
            rule.HeaderNoExtra(definition),
            rule.HeaderNoDuplicate(definition),
            rule.HeaderNoMissing(definition)
        ])


class File(DataValidator):
    def __init__(self, layouts: Union[Layout, List[Layout]], **kwargs):
        super().__init__(**kwargs)
        self.layouts = [layouts] if isinstance(layouts, Layout) else layouts
        patterns = [x.pattern for x in self.layouts]

        self.rules.extend([
            rule.FileExists(),
            rule.FileNameMatchesPattern(patterns),
            rule.FileNameMatchesOnePattern(patterns)
        ])

    def check_rules(self, file: Union[str, Path]):
        # first check file rules before attempting to read data
        p = Path(file) if isinstance(file, str) else file
        errors = super().check_rules(p)
        if errors:  # abort checks if there are any file errors
            return errors

        for layout in self.layouts:
            if re.fullmatch(layout.pattern, p.name):
                definition = layout.definition

        # noinspection PyUnboundLocalVariable
        if not definition:
            raise Exception("Something went terribly wrong")

        with open(p) as f:
            # noinspection PyUnboundLocalVariable
            names = list(definition.keys())
            types = list(definition.values())
            for rix, row in enumerate(csv.reader(f)):
                if rix == 0:  # abort checks if there are any header errors
                    errors.extend(Header(definition).check_rules(row))
                    if errors:
                        return errors
                else:
                    row_check = Row(definition).check_rules(row)
                    if row_check:
                        errors.extend([
                            f'row {str(rix + 1)}: {x}' for x in row_check
                        ])
                        continue  # if there are errors in row, skip cell checks in row
                    for cix, cell in enumerate(row):
                        errors.extend([
                            f'row {str(rix + 1)} col {str(cix + 1)} ({names[cix]}): {x}'
                            for x in types[cix].check_rules(cell)
                        ])
