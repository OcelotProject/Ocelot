# -*- coding: utf-8 -*-
from ocelot.transformations.parameterization.validation import (
    parameter_names_are_unique,
    every_exchange_with_formula_has_a_variable_name,
)
from ocelot.errors import ParameterizationError
import pytest


def test_parameter_names_are_unique():
    data = [{'parameters': [
        {
            'name': 'foo',
            'variable': 'bar'
        }, {
            'name': 'foo',
            'variable': 'baz'
        }
    ]}]
    assert parameter_names_are_unique(data)

def test_parameter_names_are_unique_error():
    data = [{'parameters': [
        {
            'variable': 'foo'
        }, {
            'variable': 'foo'
        }
    ]}]
    with pytest.raises(ParameterizationError):
        parameter_names_are_unique(data)
