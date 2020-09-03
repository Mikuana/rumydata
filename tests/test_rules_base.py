import pytest

from rumydata._base import _BaseRule
from rumydata.exception import UrNotMyDataError


def recurse_subclasses(class_to_recurse):
    def generator(x):
        for y in x.__subclasses__():
            for z in generator(y):
                yield z
        yield x

    return list(generator(class_to_recurse))


@pytest.mark.parametrize('rule', recurse_subclasses(_BaseRule))
def test_rule_exception(rule):
    """ All rules have a UrNotMyDataError type """
    assert issubclass(rule.rule_exception(), UrNotMyDataError)


@pytest.mark.parametrize('rule', recurse_subclasses(_BaseRule))
def test_rule_exception_message(rule):
    """ All rule exceptions are returned as UrNotMyData subclass """
    exc = rule(*rule._default_args)._exception_msg()
    assert issubclass(type(exc), UrNotMyDataError)


@pytest.mark.parametrize('rule', recurse_subclasses(_BaseRule))
def test_rule_default_args(rule):
    """ All rule default arguments are a tuple """
    assert isinstance(rule._default_args, tuple)


@pytest.mark.parametrize('rule', recurse_subclasses(_BaseRule))
def test_rule_explain(rule):
    """ All rule explanations return a string  """
    assert isinstance(rule(*rule._default_args)._explain(), str)


def test_base_prepare():
    r = _BaseRule()._prepare('x')
    assert isinstance(r, tuple)
    assert r[0] == 'x'
