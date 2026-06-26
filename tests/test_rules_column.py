import pytest

from rumydata.rules import column
from rumydata.rules.column import Rule


def recurse_subclasses(class_to_recurse):
    def generator(x):
        for y in x.__subclasses__():
            yield from generator(y)
        yield x

    return list(generator(class_to_recurse))


@pytest.mark.parametrize('rule', recurse_subclasses(Rule))
def test_rule_prepare(rule):
    """
    All column preparation must accept a tuple of a value and a dictionary with
    comparison values that may be required.
    """
    r = rule(*rule._default_args)
    prep = r._prepare(['x', 'y'])
    assert isinstance(prep, tuple)
    assert isinstance(prep[0], list)


@pytest.mark.parametrize('value,expected', [
    (['1', '2', '3'], True),
    (['1', '1', '3'], False),
    (['', '', '1'], True),
    (['', '1', '1'], False)
])
def test_unique(value: list, expected: bool):
    r = column.Unique()
    assert r._evaluator()(*r._prepare(value)) is expected
