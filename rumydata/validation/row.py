from rumydata import rule
from rumydata.validation import Cell


class Header(Cell):
    def __init__(self, definition, **kwargs):
        super().__init__(**kwargs)

        self.rules.extend([
            rule.HeaderColumnOrder(definition),
            rule.HeaderNoExtra(definition),
            rule.HeaderNoDuplicate(definition),
            rule.HeaderNoMissing(definition)
        ])
