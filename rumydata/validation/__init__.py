from rumydata import rule
from rumydata import exception


class BaseValidator:
    def __init__(self, rules: list = None):
        self.rules = rules or []
        self.descriptors = {}

    def check(self, value):
        errors = []
        for r in self.rules:
            # noinspection PyBroadException
            try:
                if not r.evaluator()(value):
                    errors.append(r.exception())
            except Exception as e:  # get type, and rewrite safe message
                e = type(e)
                errors.append(e(
                    f'Error while attempting check if {str(r.exception())}')
                )
        return errors

    def digest(self):
        x = [f'{k}: {v}' if v else k for k, v in self.descriptors.items()]
        y = [x.explain() for x in self.rules]
        return x + y


class DataType(BaseValidator):
    def __init__(self, nullable=False, rules: list = None):
        super().__init__(rules)
        self.nullable = nullable

        if not self.nullable:
            self.rules.append(rule.NotNull)

    def check(self, value):
        # if data is nullable and value is empty, skip all checks
        if self.nullable and value == '':
            pass
        else:
            e = super().check(value)
            if e:
                return exception.CellError(errors=e)

    def digest(self):
        dig = super().digest()
        if self.nullable:
            dig.append('Nullable')
        return dig
