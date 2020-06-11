from collections import namedtuple

from rumydata.exception import NullValueError, ValueComparisonError

Check = namedtuple('Check', ['func', 'err', 'msg'])
DataDefinition = namedtuple('DataDefinition', ['pattern', 'definition'])


class BaseValidator:
    def __init__(self, **kwargs):
        self.attributes = {}
        self.nullable = kwargs.get('nullable', False)
        self.checks = []
        if not self.nullable:
            self.checks.append(
                Check(lambda x: x != '', NullValueError, 'Value is empty/blank')
            )

        self.compare = kwargs.get('compare')
        if self.compare:
            self.checks.append(Check(
                self.compare.compare(), ValueComparisonError,
                f'Value is not {self.compare.__class__.__name__} to '
                f'{str(self.compare.compared_to)}'
            ))

    def check_errors(self, value):
        errors = []
        if self.nullable and value == '':  # if type is nullable and value is empty, skip checks
            return errors
        for check in self.checks:
            # noinspection PyBroadException
            try:
                if not check.func(value):
                    errors.append(check.err(check.msg))
            except Exception as e:  # capture type, and rewrite message to be safe
                e = type(e)
                errors.append(e(f'Error while attempting check if {check.msg}'))
        return errors

    def attribute_digest(self):
        attributes = self.attributes

        if self.nullable:
            attributes['Nullable'] = None
        if self.compare:
            attributes['Rule'] = self.compare.description()

        return [f'{k}: {v}' if v else k for k, v in attributes.items()]


class Comparison:
    language = 'N/A'

    def __init__(self, compared_to):
        self.compared_to = compared_to

    def description(self):
        return f'{self.language} {str(self.compared_to)}'


class GT(Comparison):
    """ Greater Than comparison """
    language = 'greater than'

    def compare(self):
        return lambda x: float(x) > self.compared_to


class GTE(Comparison):
    """ Greater Than or Equal comparison """
    language = 'greater than or equal to'

    def compare(self):
        return lambda x: float(x) >= self.compared_to


class ET(Comparison):
    """ Equal To comparison """
    language = 'equal to'

    def compare(self):
        return lambda x: float(x) == self.compared_to


class LOE(Comparison):
    """ Less Than or Equal comparison """
    language = 'less than or equal to'

    def compare(self):
        return lambda x: float(x) <= self.compared_to


class LT(Comparison):
    """ Less Than comparison """
    language = 'less than'

    def compare(self):
        return lambda x: float(x) < self.compared_to
