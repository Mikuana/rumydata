from pathlib import Path
from re import compile
from typing import Union, Pattern


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

    # def check(self, file: Union[str, Path], **kwargs):
    #     p = Path(file) if isinstance(file, str) else file
    #     f = File(self, **kwargs)
    #     errors = f.__check__(p)
    #     assert not errors, str(errors)
