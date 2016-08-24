# -*- coding: utf-8 -*-
from ocelot.errors import InvalidTransformationFunction
from ocelot.utils import get_function_meta, validate_configuration
import functools
import pytest


@pytest.fixture
def func():
    def f(some_arg=1):
        """A docstring"""
    f.__table__ = "Some more"
    return f

def test_get_metdata(func):
    metadata = get_function_meta(func)
    assert metadata['name'] == 'f'
    assert metadata['description'] == "A docstring"
    assert metadata['table'] == "Some more"

def test_get_metadata_partial(func):
    curried = functools.partial(func, some_arg=2)
    metadata = get_function_meta(curried)
    assert metadata['name'] == 'f'
    assert metadata['description'] == "A docstring"
    assert metadata['table'] == "Some more"

def test_valid_configuration(func):
    assert validate_configuration([func, func])
    assert validate_configuration([[func, func]])

def test_invalid_configuration():
    with pytest.raises(InvalidTransformationFunction):
        validate_configuration([1])
    with pytest.raises(InvalidTransformationFunction):
        validate_configuration([[1]])
