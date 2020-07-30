from dataclasses import dataclass

from rumydata import exception as ex


class BaseRule:
    """ Base class for defining data type rules """
    exception_class = ex.UrNotMyDataError

    def prepare(self, data) -> tuple:
        return data,

    def evaluator(self):
        """
        :return: a function which expects to evaluate to True if the value
        provided to the function meets the rule.
        """
        return lambda x: False  # default to failing evaluation if not overwritten

    def exception_msg(self):
        """
        :return: a sanitized error message which is specific to the function,
        contains no direct link to the value that was checked.
        """
        return self.exception_class(self.explain())

    def explain(self) -> str:
        """
        :return: an explanation of the rule that is applied
        """
        return "default rule explanation"


class BaseSubject:
    def __init__(self, rules: list = None):
        self.rules = rules or []
        self.descriptors = {}

    def __check__(self, data, **kwargs):
        errors = []
        restrict = kwargs.get('restrict', True)
        for r in self.rules:
            # noinspection PyBroadException
            try:
                if restrict or issubclass(type(r), restrict):
                    x = r.prepare(data)
                    e = r.evaluator()(*x)
                    if not e:
                        errors.append(r.exception_msg())
            except Exception as e:  # get type, and rewrite safe message
                errors.append(r.exception_class(
                    f'raised {e.__class__.__name__} while checking if value {r.explain()}')
                )
        return errors

    def digest(self):
        x = [f'{k}: {v}' if v else k for k, v in self.descriptors.items()]
        y = [x.explain() for x in self.rules]
        return x + y

    def list_errors(self, value, **kwargs):
        return list(self.flatten_exceptions(self.__check__(value, **kwargs)))

    def has_error(self, value, error, **kwargs):
        return error in [x.__class__ for x in self.list_errors(value, **kwargs)]

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


@dataclass
class CellData:
    value: str
    compare: dict = None


class Columns:
    def __init__(self, definition: dict, **kwargs):
        """
        Defines the layout of a tabular file.

        :param definition: dictionary of column names with DataType definitions
        """

        self.definition = definition
        self.length = len(definition)
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

    def comparison_columns(self):
        compares = set()
        for v in self.definition.values():
            compares.update(v.comparison_columns())
        return compares
