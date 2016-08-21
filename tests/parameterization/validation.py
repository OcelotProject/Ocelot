# -*- coding: utf-8 -*-
from ocelot.transformations.parameterization.validation import (
    variable_names_are_unique,
)
from ocelot.errors import ParameterizationError
import pytest


def test_variable_names_are_unique():
    data = [{
        'exchanges': [{'variable': 'bar'}],
        'parameters': [{'variable': 'baz'}]
    }]
    assert variable_names_are_unique(data)

def test_variable_names_are_unique_error():
    data = [{
        'exchanges': [{
            'production volume': {'variable': 'foo'}
        }],
        'parameters': [{'variable': 'foo'}]
    }]
    with pytest.raises(ParameterizationError):
        variable_names_are_unique(data)
