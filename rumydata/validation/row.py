from rumydata import rule
from rumydata.validation import DataType


class Row(DataType):
    def __init__(self, definition, **kwargs):
        super().__init__(**kwargs)
        expected_length = len(list(definition.keys()))

        self.rules.extend([
            rule.LengthLTE(expected_length),
            rule.LengthET(expected_length),
            rule.LengthGTE(expected_length)
        ])


class Header(DataType):
    def __init__(self, definition, **kwargs):
        super().__init__(**kwargs)

        self.rules.extend([
            rule.HeaderColumnOrder(definition),
            rule.HeaderNoExtra(definition),
            rule.HeaderNoDuplicate(definition),
            rule.HeaderNoMissing(definition)
        ])
