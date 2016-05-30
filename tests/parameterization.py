# -*- coding: utf-8 -*-
from ocelot.transformations import parameter_names_are_unique
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
    assert parameter_names_are_unique(data, None)


def test_parameter_names_are_unique_error():
    data = [{'parameters': [
        {
            'variable': 'foo'
        }, {
            'variable': 'foo'
        }
    ]}]
    with pytest.raises(ParameterizationError):
        parameter_names_are_unique(data, None)
