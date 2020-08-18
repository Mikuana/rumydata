"""
rumydata base object submodule

This submodule contains the base objects that are used by other modules in this
package. This is not intended for use by end-users.
"""

from rumydata import exception as ex


class BaseRule:
    """
    Base class for defining data type rules.

    This class contains the default methods that can be used to stub out all of
    the rule types contained in the rules submodule.
    """
    exception_class = ex.UrNotMyDataError

    def prepare(self, data) -> tuple:
        """
        Handle data object for pre-processing prior to evaluation

        This method solves two problems that exist in the package.

        The first, is that different rule types expect different kinds of data,
        but the subject (e.g. cell, row, column) cannot anticipate what data
        will be needed by each rule. By including a prepare method, and calling
        it to process the data into the evaluator, we can allow multiple types
        of rules which expect different types of data objects to co-exist.

        The second, is that we can perform undifferentiated heavy lifting that
        might be cumbersome in the evaluator method, instead of repeating
        fragments of code multiple times in the evaluator.

        :param data: an undefined data object
        :return: a tuple, which contains some version of the provided data after
          processing
        """
        return data,

    def evaluator(self):
        """
        Generate a function that will perform evaluation of prepared data.

        The evaluator method provides the caller with a function that can be
        used to evaluate a data object which was pre-processed by this classes
        prepare method. By modifying the lambda function that is returned by
        this method, the user is modifying the actual rule that will be applied
        to any data which is covered by this rule.

        Because the function return by this method is a class method, the user
        has the opportunity to drive change in the returned function by changing
        the arguments of this classes constructor.

        :return: a function which expects to evaluate to True if the value
        provided to the function meets the rule.
        """
        return lambda x: False  # default to failing evaluation if not overwritten

    def exception_msg(self) -> ex.UrNotMyDataError:
        """
        Validation exception message

        Generates an exception from the exception_class property with a
        sanitized error message that explicitly avoids showing the specific data
        that failed the validation.
        """
        return self.exception_class(self.explain())

    def explain(self) -> str:
        """
        Rule explanation message

        An explanation of the rule that is being applied to the provided data.
        The explanation should be written in a way which clearly links it to the
        evaluation rule. It is very important that the description of the rule
        be clear enough that the user would understand why this particular rule
        failed once they compare the description to their data.
        """
        return "default rule explanation"


class BaseSubject:
    def __init__(self, rules: list = None):
        self.rules = rules or []
        self.descriptors = {}

    def __check__(self, data, rule_type, **kwargs):
        errors = []
        if not self.rules:
            return [ex.NoRulesDefinedError()]

        for r in self.rules:
            # noinspection PyBroadException
            try:
                if issubclass(type(r), rule_type):
                    x = r.prepare(data)
                    e = r.evaluator()(*x)
                    if not e:
                        errors.append(r.exception_msg())
            except Exception as e:  # get type, and rewrite safe message
                errors.append(r.exception_class(
                    f'raised {e.__class__.__name__} while checking if value {r.explain()}')
                )
        return errors

    def __list_errors__(self, value, **kwargs):
        return list(self.flatten_exceptions(self.__check__(value, **kwargs)))

    def __has_error__(self, value, error, **kwargs):
        return error in [x.__class__ for x in self.__list_errors__(value, **kwargs)]

    def digest(self):
        x = [f'{k}: {v}' if v else k for k, v in self.descriptors.items()]
        y = [x.explain() for x in self.rules]
        return x + y

    @classmethod
    def flatten_exceptions(cls, error):
        if isinstance(error, list):
            for el in error:
                yield cls.flatten_exceptions(el)
        elif issubclass(error.__class__, ex.UrNotMyDataError):
            yield error
            for el in error.errors:
                for x in cls.flatten_exceptions(el):
                    yield x
        else:
            yield error
