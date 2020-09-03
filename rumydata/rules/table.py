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


class MaxError(Rule):
    """ Row errors returned while checking file do not exceed a limit """

    _default_args = (1,)

    def __init__(self, max_row_errors):
        super().__init__()
        self.max_row_errors = max_row_errors

    def _explain(self) -> str:
        return f'files returned row errors than allowed: {self.max_row_errors}'
