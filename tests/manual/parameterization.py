# -*- coding: utf-8 -*-
from ocelot.transformations.parameterization import *
from ocelot.errors import ParameterizationError
from bw2parameters import ParameterSet


parameterized_ds = {
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

def test_valid_parameterized_ds():
    if not ParameterizedDataset(parameterized_ds):
        raise ValueError

def test_extracted_data():
    ds = {
        'radius': {'formula': 'blueberry_size * number_blueberries'},
        'pie': {'amount': 3.1415926535},
        'blueberry_volume': {'amount': 17},
        'circle': {'formula': 'pie * radius ** 2'},
        'blueberry_density': {'amount': 1},
        'number_blueberries': {'amount': 42},
        'blueberry_size': {'formula': 'blueberry_density * blueberry_volume'}
    }
    ParameterSet(ds)

def test_update_dataset():
    expected = {
        'exchanges': [{
            'amount': 3.1415926535,
            'variable': 'pie',
            'production volume': {
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
    result = ParameterizedDataset(parameterized_ds).update_dataset()
    assert result == expected


def run_all_parameterization():
    test_valid_parameterized_ds()
    test_extracted_data()
    test_update_dataset()
