import re
from pathlib import Path
from typing import Union, List

from rumydata import exception as ex
from rumydata.base import BaseRule


class Rule(BaseRule):

    def prepare(self, data: Union[str, Path]) -> tuple:
        return data,


class FileExists(Rule):
    exception_class = FileNotFoundError

    def evaluator(self):
        return lambda x: Path(x).exists()

    def explain(self) -> str:
        return 'files must exist'


class FileNameMatchesPattern(Rule):
    exception_class = ex.FilePatternError

    def __init__(self, pattern: Union[re.Pattern, List[re.Pattern]]):
        self.patterns = [pattern] if isinstance(pattern, re.Pattern) else pattern

    def evaluator(self):
        return lambda x: any([p.fullmatch(Path(x).name) for p in self.patterns])

    def explain(self) -> str:
        return 'files name must match a pattern provided in the layout'


class FileNameMatchesOnePattern(Rule):
    exception_class = ex.UrNotMyDataError

    def __init__(self, patterns: list):
        self.patterns = patterns

    def evaluator(self):
        return lambda x: sum([
            True if p.fullmatch(Path(x).name) else False for p in self.patterns
        ]) <= 1

    def explain(self) -> str:
        return 'files cannot match multiple patterns provided in the layout'
