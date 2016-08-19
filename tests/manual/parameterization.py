# -*- coding: utf-8 -*-
from ocelot.transformations.parameterization import extract_named_parameters, recalculate
from ocelot.errors import ParameterizationError
from bw2parameters import ParameterSet
from copy import deepcopy


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

def test_extract_named_parameters():
    expected = {
        'radius': {'formula': 'blueberry_size * number_blueberries'},
        'pie': {'amount': 3.1415926535},
        'blueberry_volume': {'amount': 17},
        'circle': {'formula': 'pie * radius ** 2'},
        'blueberry_density': {'amount': 1},
        'number_blueberries': {'amount': 42},
        'blueberry_size': {'formula': 'blueberry_density * blueberry_volume'}
    }
    assert extract_named_parameters(deepcopy(parameterized_ds)) == expected

def test_recalculate():
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
            'amount': 3.1415926535 * (17 * 42) ** 2,
            'properties': [{
                'variable': 'radius',
                'amount': 17 * 42,
                'formula': 'blueberry_size * number_blueberries'
            }]
        }],
        'parameters': [{
            'variable': 'blueberry_size',
            'amount': 17,
            'formula': 'blueberry_density * blueberry_volume'
        }, {
            'variable': 'blueberry_density',
            'amount': 1
        }]
    }
    assert recalculate(deepcopy(parameterized_ds)) == expected


def run_all_parameterization():
    test_extract_named_parameters()
    test_recalculate()
