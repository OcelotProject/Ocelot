# -*- coding: utf-8 -*-
from ocelot.transformations.cutoff.combined import combined_production
from copy import deepcopy


cp_dataset = {
    'name': 'a',
    'location': 'b',
    'exchanges': [{
        'type': 'reference product',
        'amount': 2,
        'variable': "first",
        'name': '',
    }, {
        'type': 'reference product',
        'amount': 3,
        'variable': 'second',
        'name': '',
    }, {
        'type': 'from technosphere',
        'formula': 'some_parameter * 2',
    }, {
        'type': 'to environment',
        'formula': 'some_parameter / 2',
    }],
    'parameters': [{
        'variable': 'some_parameter',
        'formula': '(first + second) * 10',
    }]
}

def test_combined_production_without_byproducts():
    expected = [{
        'name': 'a',
        'location': 'b',
        'exchanges': [{
            'type': 'reference product',
            'amount': 2,
            'variable': 'first',
            'name': '',
        }, {
            'type': 'dropped product',
            'amount': 0.0,
            'variable': 'second',
            'name': '',
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
        'name': 'a',
        'location': 'b',
        'exchanges': [{
            'type': 'reference product',
            'amount': 3,
            'variable': 'second',
            'name': '',
        }, {
            'type': 'dropped product',
            'amount': 0.0,
            'variable': 'first',
            'name': '',
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

def test_combined_production_repair_distributions():
    original = {
        'name': 'a',
        'location': 'b',
        'exchanges': [{
            'amount': 1,
            'type': 'reference product',
            'name': '',
        }, {
            'type': 'to environment',
            'amount': 1.0,
            'formula': "first * 2",
            'uncertainty': {
                'type': 'lognormal',
                'mu': 0,
                'variance with pedigree matrix': 0.15
            }
        }],
        'parameters': [{
            'variable': 'first',
            'amount': 0,
        }]
    }
    expected = [{
        'name': 'a',
        'location': 'b',
        'exchanges': [{
            'amount': 1,
            'type': 'reference product',
            'name': '',
        }, {
            'type': 'to environment',
            'amount': 0,
            'formula': "first * 2",
        }],
        'parameters': [{
            'variable': 'first',
            'amount': 0,
        }]
    }]
    assert combined_production(original) == expected


def run_all_combined():
    test_combined_production_without_byproducts()
    test_combined_production_repair_distributions()
