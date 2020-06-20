from re import compile, Pattern
from typing import Union

from rumydata.rule import NotNull


class Layout:
    def __init__(self, definition: dict, pattern: Union[str, Pattern] = None, **kwargs):
        if isinstance(pattern, str):
            self.pattern = compile(pattern)
        else:
            self.pattern = pattern

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


class BaseValidator:
    def __init__(self, rules: list = None):
        self.rules = rules or []
        self.descriptors = {}

    def check_rules(self, value):
        errors = []
        for rule in self.rules:
            # noinspection PyBroadException
            try:
                if not rule.evaluator()(value):
                    errors.append(rule.exception())
            except Exception as e:  # get type, and rewrite safe message
                e = type(e)
                errors.append(e(
                    f'Error while attempting check if {str(rule.exception())}')
                )
        return errors

    def digest(self):
        x = [f'{k}: {v}' if v else k for k, v in self.descriptors.items()]
        y = [x.explain() for x in self.rules]
        return x + y


class DataValidator(BaseValidator):
    def __init__(self, nullable=False, rules: list = None):
        super().__init__(rules)
        self.nullable = nullable

        if not self.nullable:
            self.rules.append(NotNull)

    def check_rules(self, value):
        # if data is nullable and value is empty, skip all checks
        if self.nullable and value == '':
            return []
        else:
            return super().check_rules(value)

    def digest(self):
        dig = super().digest()
        if self.nullable:
            dig.append('Nullable')
        return dig
