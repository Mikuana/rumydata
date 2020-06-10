from collections import namedtuple

from rumydata.exception import NullValueError

Check = namedtuple('Check', ['func', 'err', 'msg'])
DataDefinition = namedtuple('DataDefinition', ['pattern', 'definition'])


class BaseValidator:
    def __init__(self, **kwargs):
        self.checks = []
        if not kwargs.get('nullable', False):
            self.checks.append(
                Check(lambda x: x != '', NullValueError, 'Value is empty/blank')
            )

    def check_errors(self, value):
        errors = []
        for check in self.checks:
            # noinspection PyBroadException
            try:
                if not check.func(value):
                    errors.append(check.err(check.msg))
            except Exception as e:  # capture type, and rewrite message to be safe
                e = type(e)
                errors.append(e(f'Error while attempting check if {check.msg}'))
        return errors
