# -*- coding: utf-8 -*-
from ocelot.utils import get_function_meta
from ocelot.wrapper import TransformationWrapper
import pytest


@pytest.fixture
def func():
    def f(dataset):
        """A docstring"""
        return [dataset]

    f.__table__ = "Something about a table"
    return f

def test_setup(func):
    metadata = get_function_meta(func)
    assert metadata['name'] == 'f'
    assert metadata['description'] == "A docstring"
    assert metadata['table'] == "Something about a table"

def test_metadata(func):
    metadata = get_function_meta(TransformationWrapper(func))
    assert metadata['name'] == 'f'
    assert metadata['description'] == "A docstring"
    assert metadata['table'] == "Something about a table"

def test_correct_unrolling(func):
    funky = lambda x: [1,2,3]
    filter_func = lambda x: x == 2
    wrapped = TransformationWrapper(funky, filter_func)
    assert wrapped([1, 2, 3]) == [1, 1, 2, 3, 3]
