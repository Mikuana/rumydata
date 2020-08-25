"""
rumydata file rules

These rules are applied to entire files and are generally not meant to be used
directly. These accomplish things like confirming a file exists, that it matches
a particular regex pattern, etc.
"""

import re
from pathlib import Path
from typing import Union, List

from rumydata import exception as ex
from rumydata.base import BaseRule


class Rule(BaseRule):
    """ File Rule """

    def _prepare(self, data: Union[str, Path]) -> tuple:
        return data,


class FileExists(Rule):
    """ File exists Rule """

    exception_class = FileNotFoundError

    def _evaluator(self):
        return lambda x: Path(x).exists()

    def _explain(self) -> str:
        return 'files must exist'


class FileNameMatchesPattern(Rule):
    """ File name matches regex pattern Rule """

    exception_class = ex.FilePatternError

    def __init__(self, pattern: Union[re.Pattern, List[re.Pattern]]):
        self.patterns = [pattern] if isinstance(pattern, re.Pattern) else pattern

    def _evaluator(self):
        return lambda x: any([p.fullmatch(Path(x).name) for p in self.patterns])

    def _explain(self) -> str:
        return 'files name must match a pattern provided in the layout'


class FileNameMatchesOnePattern(Rule):
    """ File name matches exactly one pattern Rule """
    exception_class = ex.UrNotMyDataError

    def __init__(self, patterns: list):
        self.patterns = patterns

    def _evaluator(self):
        return lambda x: sum([
            True if p.fullmatch(Path(x).name) else False for p in self.patterns
        ]) <= 1

    def _explain(self) -> str:
        return 'files cannot match multiple patterns provided in the layout'
