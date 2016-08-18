# -*- coding: utf-8 -*-
from ocelot.transformations.parameterization import *
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


@pytest.fixture(scope="function")
def parameterized_ds():
    return {
        'exchanges': [{
            'amount': 3.1415926535,
            'variable': 'pie',
            'production volume': {  # Nonsensical but should work
                'variable': 'number_blueberries',
                'amount': 42
            },
            'properties': [{
                'variable': 'blueberry_volume',
                'amount': 17
            }]
        }, {
            'variable': 'circle',
            'formula': 'pie * radius ** 2',
            'properties': [{
                'variable': 'radius',
                'formula': 'blueberry_size * number_blueberries'
            }]
        }],
        'parameters': [{
            'variable': 'blueberry_size',
            'formula': 'blueberry_density * blueberry_volume'
        }, {
            'variable': 'blueberry_density',
            'amount': 1
        }]
    }

def test_iterate_all_parameters(parameterized_ds):
    generator = iterate_all_parameters(parameterized_ds)
    assert next(generator) == parameterized_ds['exchanges'][0]
    assert next(generator) == parameterized_ds['exchanges'][0]['production volume']
    assert next(generator) == parameterized_ds['exchanges'][0]['properties'][0]
    assert next(generator) == parameterized_ds['exchanges'][1]
    assert next(generator) == parameterized_ds['exchanges'][1]['properties'][0]
    assert next(generator) == parameterized_ds['parameters'][0]
    assert next(generator) == parameterized_ds['parameters'][1]
