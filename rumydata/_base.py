"""
rumydata base object submodule

This submodule contains the base objects that are used by other modules in this
package. This is not intended for use by end-users.
"""

from typing import List, Union

from rumydata import exception as ex


class _BaseRule:
    """
    Base class for defining data type rules.

    This class contains the default methods that can be used to stub out all of
    the rule types contained in the rules submodule.
    """
    _default_args = tuple()  # a default set of positional args for testing

    def __init__(self):
        pass

    @staticmethod
    def _pre_process(data: tuple) -> tuple:
        """
        Handle data object for rule-type processing prior to evaluation

        This processing is meant to be invoked once per check call, rather than
        once for each rule checked. It handles pre-processing that will apply to
        all rules.

        :param data: an undefined data object
        :return: a tuple, which contains some version of the provided data after
          processing
        """
        return data

    @classmethod
    def rule_exception(cls):
        return type(f'{cls.__name__}Error', (ex.UrNotMyDataError,), {})

    def _prepare(self, data) -> tuple:
        """
        Handle data object for rule-specific processing prior to evaluation

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

    def _evaluator(self):
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

    def _exception_msg(self) -> ex.UrNotMyDataError:
        """
        Validation exception message

        Generates an exception from the rule_exception method with a
        sanitized error message that explicitly avoids showing the specific data
        that failed the validation.
        """
        return self.rule_exception()(self._explain())

    def _explain(self) -> str:
        """
        Rule explanation message

        An explanation of the rule that is being applied to the provided data.
        The explanation should be written in a way which clearly links it to the
        evaluation rule. It is very important that the description of the rule
        be clear enough that the user would understand why this particular rule
        failed once they compare the description to their data.
        """
        return "default rule explanation"


class _BaseSubject:
    """
    Base class for defining data subjects.

    This class serves as the basis for the definition of the Field, Layout, and
    File classes. It provides the basic framework for performing checks of rules
    and reporting errors in a way that can be easily collected.
    """

    _default_args = tuple()  # a default set of positional args for testing

    def __init__(self, rules: List[_BaseRule] = None):
        """
        Base subject constructor

        :param rules: a list of rules which should be applied when performing a
        check of data against this object. Rules must all be subclasses of the
        BaseRule.
        """
        self.rules = rules or []
        self.descriptors = {}

    def _check(self, data, rule_type, **kwargs) -> Union[ex.UrNotMyDataError, List[ex.UrNotMyDataError], None]:
        """
        Check data against specified rule types

        This is the core method used to evaluate data against a subject defined
        by this class.

        :param data: an object which conforms to the `prepare` method of the
            class specified in the rule_type parameter
        :param rule_type: a Rule class belonging to one of the submodules in the
            rules module (e.g. rumydata.rules.cell.Rule). This controls the
            types of rules that the provided data will be checked against.
        :return: a list of any errors that were raised while checking the data.
        """
        errors = []
        if rule_type:
            try:
                data = rule_type._pre_process(data, **kwargs)
            except Exception as e:
                msg = f'raised {e.__class__.__name__} while preprocessing data'
                if ex.debug():
                    msg += f' [DEBUG]: {str(e)}'
                return [ex.PreProcessingError(msg)]

        for r in self.rules:
            # noinspection PyBroadException
            try:
                if issubclass(type(r), rule_type):
                    x = r._prepare(data)
                    e = r._evaluator()(*x)
                    if not e:
                        errors.append(r._exception_msg())
            except Exception as e:  # get type, and rewrite safe message
                msg = f'raised {e.__class__.__name__} while checking if value {r._explain()}'
                if ex.debug():
                    msg += f' [DEBUG]: {str(e)}'
                errors.append(r.rule_exception()(msg))
        return errors

    def _list_errors(self, value, **kwargs) -> List[ex.UrNotMyDataError]:
        """
        Flatten nested errors into a list

        This method is a convenience wrapper to perform a check of certain data,
        then flatten the nested errors into a simple list

        :param value: value to be checked
        :return: a list of exceptions raised during check of the provided value
        """
        return list(self._flatten_exceptions(self._check(value, **kwargs)))

    def _has_error(self, value, error, **kwargs) -> bool:
        """

        Check flattened errors for a specific exception type

        This method is a convenience wrapper for testing which determines if the
        nested structure of errors returned by a check includes a specified
        error type.

        :param value: value to be checked.
        :param error: a subclass of UrNotMyDataError which you are checking for.
        :return: a boolean indicator of whether the specified error type was
            returned in the nested structure when checking the provided value.
        """
        # errors must be checked by name since they are generated dynamically for each rule and
        return error.__name__ in [type(x).__name__ for x in self._list_errors(value, **kwargs)]

    def _digest(self) -> List[str]:
        """
        Subject descriptor list

        A method to generate a list of descriptors for this subject, based upon
        the explain method of the rules associated with this subject, as well as
        any additional descriptors set in property of this object

        :return: a list of strings which are used to build a comprehensive
            description of the definition of this subject.
        """
        x = [f'{k}: {v}' if v else k for k, v in self.descriptors.items()]
        y = [x._explain() for x in self.rules]
        return x + y

    @classmethod
    def _flatten_exceptions(cls, error):
        """
        Nested exception generator function

        This method generates a set of nested errors that may exist in a
        UrNotMyData error, as a simple list of errors.

        The design of error reporting creates a nested structure of errors;
        FileError has RowErrors and ColumnErrors, and RowErrors have CellErrors.
        While this is ideal for rolling up errors into a single, comprehensive
        report, this structure makes searching for the presence of particular
        errors difficult.

        This method provides a way to easily search a nested tree of errors for
        a specific error. Essentially, iterates through a list of errors,
        checking to see if any of those errors contain additional errors, then
        continuing to recurse until all errors have been yielded.
        """
        yield error
        for el in error._errors:
            for x in cls._flatten_exceptions(el):
                yield x
