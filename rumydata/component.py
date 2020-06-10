from collections import namedtuple

Check = namedtuple('Check', ['func', 'err', 'msg'])
DataDefinition = namedtuple('DataDefinition', ['pattern', 'definition'])


class BaseValidator:
    checks = []

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
