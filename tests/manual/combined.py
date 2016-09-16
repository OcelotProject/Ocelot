# -*- coding: utf-8 -*-
from ocelot.transformations.cutoff.combined import combined_production
from copy import deepcopy

cp_dataset = {
    'exchanges': [{
        'type': 'reference product',
        'amount': 2,
        'variable': "first",
    }, {
        'type': 'reference product',
        'amount': 3,
        'variable': 'second'
    }, {
        'type': 'from technosphere',
        'formula': 'some_parameter * 2'
    }, {
        'type': 'to environment',
        'formula': 'some_parameter / 2'
    }],
    'parameters': [{
        'variable': 'some_parameter',
        'formula': '(first + second) * 10'
    }]
}

def test_combined_production_without_byproducts():
    expected = [{
        'exchanges': [{
            'type': 'reference product',
            'amount': 2,
            'variable': 'first',
        }, {
            'type': 'dropped product',
            'amount': 0.0,
            'variable': 'second',
        }, {
            'amount': ((2 + 0) * 10) * 2,
            'formula': 'some_parameter * 2',
            'type': 'from technosphere',
        }, {
            'amount': ((2 + 0) * 10) / 2,
            'formula': 'some_parameter / 2',
            'type': 'to environment',
        }],
        'parameters': [{
            'amount': 20.0,
            'formula': '(first + second) * 10',
            'variable': 'some_parameter',
        }]
    }, {
        'exchanges': [{
            'type': 'reference product',
            'amount': 3,
            'variable': 'second',
        }, {
            'type': 'dropped product',
            'amount': 0.0,
            'variable': 'first',
        }, {
            'amount': ((0 + 3) * 10) * 2,
            'formula': 'some_parameter * 2',
            'type': 'from technosphere',
        }, {
            'amount': ((0 + 3) * 10) / 2,
            'formula': 'some_parameter / 2',
            'type': 'to environment',
        }],
        'parameters': [{
            'amount': ((0 + 3) * 10),
            'formula': '(first + second) * 10',
            'variable': 'some_parameter',
        }]
    }]
    original = deepcopy(cp_dataset)
    assert combined_production(cp_dataset) == expected
    assert original == cp_dataset


def run_all_combined():
    test_combined_production_without_byproducts()
