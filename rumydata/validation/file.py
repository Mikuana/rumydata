import csv
from pathlib import Path
from re import compile
from typing import Union, Pattern

from rumydata.validation import BaseValidator
from rumydata.validation.row import rule, Header, Row


class Layout:
    def __init__(self, definition: dict, pattern: Union[str, Pattern] = None, **kwargs):
        """
        Defines the layout of a tabular file.

        :param definition: dictionary of column names with DataType definitions
        :param pattern: an optional regex pattern - provided as either a string or
        a re.Pattern class - which will be used to determine if a file matches an
        expected naming schema. This is necessary when your data set includes multiple,
        as it allows the package to determine which definition should be used to
        validate file.
        """
        if isinstance(pattern, str):
            self.pattern = compile(pattern)
        elif isinstance(pattern, Pattern):
            self.pattern = pattern
        elif not pattern:
            self.pattern = compile(r'.+')

        self.definition = definition

        self.title = kwargs.get('title')

    def digest(self):
        return [[f'Name: {k}', *v.digest()] for k, v in self.definition.items()]

    def markdown_digest(self):
        fields = f'# {self.title}' + '\n\n' if self.title else ''
        fields += '\n'.join([
            f' - **{k}**' + ''.join(['\n   - ' + x for x in v.digest()])
            for k, v in self.definition.items()
        ])
        return fields

    def check_file(self, file: Union[str, Path], **kwargs):
        p = Path(file) if isinstance(file, str) else file
        f = File(self, **kwargs)
        return f.check_rules(p)


class File(BaseValidator):
    def __init__(self, layout: Layout, **kwargs):
        super().__init__(**kwargs)
        self.layout = layout

        self.rules.extend([
            rule.FileExists(),
            rule.FileNameMatchesPattern(self.layout.pattern),
        ])

    def check_rules(self, file: Union[str, Path]):
        p = Path(file) if isinstance(file, str) else file
        errors = super().check_rules(p)  # check file-based rules first
        if errors:
            return errors

        d = self.layout.definition
        with open(p) as f:
            names = list(d.keys())
            types = list(d.values())
            for rix, row in enumerate(csv.reader(f)):
                if rix == 0:  # abort checks if there are any header errors
                    errors.extend(Header(d).check_rules(row))
                    if errors:
                        return errors
                else:
                    row_check = Row(d).check_rules(row)
                    if row_check:
                        errors.extend([
                            f'row {str(rix + 1)}: {x}' for x in row_check
                        ])
                        continue  # if there are errors in row, skip cell checks
                    for cix, cell in enumerate(row):
                        errors.extend([
                            type(x)(
                                f'row {str(rix + 1)} col {str(cix + 1)} '
                                f'({names[cix]}): {x}'
                            )
                            for x in types[cix].check_rules(cell)
                        ])
        return errors
