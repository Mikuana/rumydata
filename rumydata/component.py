from collections import namedtuple

from rumydata.rule import Nullable

Check = namedtuple('Check', ['func', 'err', 'msg'])
DataDefinition = namedtuple('DataDefinition', ['pattern', 'definition'])


class BaseValidator:
    def __init__(self, **kwargs):
        self.descriptors = {}
        self.nullable = kwargs.get('nullable', False)
        self.rules = []

        if not self.nullable:
            self.rules.append(Nullable)

        for r in kwargs.get('rules', []):
            self.rules.append(r)

    def check_rules(self, value):
        errors = []
        # if type is nullable and value is empty, skip all other checks
        if self             .nullable and value == '':
            return errors
        for rule in self.rules:
            # noinspection PyBroadException
            try:
                if not rule.evaluator()(value):
                    errors.append(rule.exception())
            except Exception as e:  # get type, and rewrite message to be safe
                e = type(e)
                errors.append(e(
                    f'Error while attempting check if {str(rule.exception())}')
                )
        return errors

    def attribute_digest(self):
        attributes = self.descriptors

        if self.nullable:
            attributes['Nullable'] = None
        # if self.compare:
        #     attributes['Rule'] = self.compare.description()

        return [f'{k}: {v}' if v else k for k, v in attributes.items()]
