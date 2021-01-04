"""
rumydata file rules

These rules are applied to entire files and are generally not meant to be used
directly. These accomplish things like confirming a file exists, that it matches
a particular regex pattern, etc.
"""
from pathlib import Path
from typing import Union

from rumydata._base import _BaseRule


class Rule(_BaseRule):
    """ File Rule """

    def _prepare(self, data: Union[str, Path]) -> tuple:
        return data,


class FileExists(Rule):
    """ File exists Rule """

    def _evaluator(self):
        return lambda x: Path(x).exists()

    def _explain(self) -> str:
        return 'files must exist'


class FileNameMatch(Rule):
    """ File name matches regex pattern """

    _default_args = ('test',)

    def __init__(self, pattern):
        super().__init__()
        self.pattern = pattern

    def _evaluator(self):
        import re
        return lambda x: re.fullmatch(self.pattern, x.name, re.IGNORECASE)

    def _explain(self) -> str:
        # TODO come up with a better way to make a 'human readable' error message for bad file name in regards to a regex pattern....
        return f'file must match naming pattern {self.pattern}'


class MaxError(Rule):
    """ Row errors returned while checking file do not exceed a limit """

    _default_args = (1,)

    def __init__(self, max_row_errors):
        super().__init__()
        self.max_row_errors = max_row_errors

    def _explain(self) -> str:
        return f'files returned row errors than allowed: {self.max_row_errors}'
