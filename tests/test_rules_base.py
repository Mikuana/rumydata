import pytest

from rumydata.base import BaseRule
from rumydata.exception import UrNotMyDataError


def recurse_subclasses(class_to_recurse) -> list:
    def generator(x):
        for y in x.__subclasses__():
            for z in generator(y):
                yield z
        yield x

    return list(generator(class_to_recurse))


@pytest.mark.parametrize('rule', [x for x in recurse_subclasses(BaseRule)])
def test_rule_exception(rule):
    """ All rules have a UrNotMyDataError type """
    assert issubclass(rule.exception_class, UrNotMyDataError)


@pytest.mark.parametrize('rule', [x for x in recurse_subclasses(BaseRule)])
def test_rule_default_args(rule):
    """ All rule default arguments are a tuple """
    assert isinstance(rule._default_args, tuple)


@pytest.mark.parametrize('rule', [x for x in recurse_subclasses(BaseRule)])
def test_rule_explain(rule):
    """ All rule explanations return a string  """
    assert isinstance(rule(*rule._default_args)._explain(), str)
