# -*- coding: utf-8 -*-
from numbers import Number
from numpy import allclose
from ocelot.io.extract_ecospold2 import generic_extractor
from ocelot.io.validate_internal import dataset_schema
from ocelot.transformations.cutoff.allocation import choose_allocation_method
from ocelot.transformations.cutoff.economic import economic_allocation
from ocelot.transformations.utils import get_single_reference_product
import os
import pytest


### Test artificial cases

@pytest.fixture(scope="function")
def no_allocation(monkeypatch):
    monkeypatch.setattr(
        'ocelot.transformations.cutoff.economic.apply_allocation_factors',
        lambda x, y: (x, y)
    )

def test_economic_allocation_outputs(no_allocation):
    dataset = {
        'exchanges': [{
            'type': 'reference product',
            'name': 'foo',
            'amount': 2,
            'properties': [{
                'name': 'price',
                'amount': 14
            }]
        }]
    }
    expected = {
        'type': 'reference product',
        'name': 'foo',
        'amount': 2,
        'properties': [{
            'name': 'price',
            'amount': 14
        }]
    }
    obj, lst = economic_allocation(dataset)
    assert obj is dataset
    assert list(lst) == [(1, expected)]

def test_allocation_factors(no_allocation):
    dataset = {'exchanges': [{
        'name': 'first',
        'type': 'reference product',
        'amount': 4,
        'properties': [{
            'name': 'price',
            'amount': 2.5
        }]
    }, {
        'name': 'second',
        'type': 'reference product',
        'amount': 10,
        'properties': [{
            'name': 'price',
            'amount': 2
        }]
    }, {
        'name': 'third',
        'type': 'biosphere',
        'amount': 30
    }]}
    obj, lst = economic_allocation(dataset)
    # Allocation by revenue; revenue is (4 * 2.5 = 10, 2 * 10 = 20) = (1/3, 2/3)
    assert [x[0] for x in lst] == [1/3, 2/3]

def test_normal_economic_allocation():
    dataset = {'exchanges': [{
        'name': 'first',
        'type': 'reference product',
        'amount': 4,
        'properties': [{
            'name': 'price',
            'amount': 2.5
        }]
    }, {
        'name': 'second',
        'type': 'reference product',
        'amount': 10,
        'properties': [{
            'name': 'price',
            'amount': 2
        }]
    }, {
        'name': 'third',
        'type': 'biosphere',
        'amount': 60
    }]}
    # Allocation by revenue; revenue is (4 * 2.5 = 10, 2 * 10 = 20) = (1/3, 2/3)
    # So biosphere amount is (20, 40)
    # Normalize to production of 1: 20 / 4, 40 / 10 = (5, 4)
    expected = [{
        'exchanges': [{
            'amount': 1.0,
            'name': 'first',
            'type': 'reference product',
            'properties': [{
                'name': 'price',
                'amount': 2.5}]
        }, {
            'amount': 0.0,
            'name': 'second',
            'type': 'dropped product',
            'properties': [{
                'name': 'price',
                'amount': 2
            }]
        }, {
            'amount': 5,
            'name': 'third',
            'type': 'biosphere',
        }]
    }, {
        'exchanges': [{
            'amount': 1.0,
            'name': 'second',
            'type': 'reference product',
            'properties': [{
                'name': 'price',
                'amount': 2
            }]
        }, {
            'type': 'dropped product',
            'amount': 0.0,
            'name': 'first',
            'properties': [{
                'name': 'price',
                'amount': 2.5
            }]
        }, {
            'type': 'biosphere',
            'name': 'third',
            'amount': 4
        }]
    }]
    assert economic_allocation(dataset) == expected


### Test real test data

@pytest.fixture(scope="module")
def cardboard():
    fp = os.path.join(os.path.dirname(__file__), "..", "data",
                      "corrugated-board.spold")
    return generic_extractor(fp)[0]

def test_load_validate_cardboard_dataset(cardboard):
    assert dataset_schema(cardboard)

def test_choice_allocation_method(cardboard):
    assert choose_allocation_method(cardboard) == "economic"

def test_allocation_function_output_valid(cardboard):
    for new_ds in economic_allocation(cardboard):
        assert dataset_schema(new_ds)

def test_allocation_cardboard(cardboard):
    """Cardboard dataset produces:

    1. corrugated board box
        * Reference product
        * Price: 0.843326883 €/kg
        * Amount: 1000 kg
        * Revenue: 843.326883 €
    2. residual softwood, wet
        * Allocatable byproduct
        * Price: 19.4156914399732 €/m3
        * Amount: 0.00209150326797386 m3
        * Revenue: 0.04060798209667605 €

    Allocation factors: 0.9999518501927914, 4.814980720846648e-05

    Elementary exchange: 0.000163 kg Propane
    Elementary exchange: 0.03 kg Nitrogen oxides
    Input: 5.95 kg potato starch
    Input: 19.9481865284974 m3 natural gas, low pressure
    Waste: 0.046 kg waste mineral oil

    """
    datasets = economic_allocation(cardboard)
    assert len(datasets) == 2

    for ds in datasets:
        assert len(ds['exchanges']) == 7
        for key, value in cardboard.items():
            if key == 'exchanges':
                continue
            else:
                assert ds[key] == value

        rp = get_single_reference_product(ds)
        if rp['name'] == 'corrugated board box':
            expected = {
                'corrugated board box': {
                    'amount': 1,
                    'type': 'reference product',
                },
                'residual softwood, wet': {
                    'amount': 0,
                    'type': 'dropped product',
                },
                'waste mineral oil': {
                    'amount': 0.9999518501927914 * 0.046 / 1000,
                },
                'natural gas, low pressure': {
                    'amount': 0.9999518501927914 * 19.9481865284974 / 1000,
                },
                'potato starch': {
                    'amount': 0.9999518501927914 * 5.95 / 1000,
                },
                'Propane': {
                    'amount': 0.9999518501927914 * 0.000163 / 1000,
                },
                'Nitrogen oxides': {
                    'amount': 0.9999518501927914 * 0.03 / 1000
                }
            }
        else:
            expected = {
                'corrugated board box': {
                    'amount': 0,
                    'type': 'dropped product',
                },
                'residual softwood, wet': {
                    'amount': 1,
                    'type': 'reference product',
                },
                'waste mineral oil': {
                    'amount': 4.814980720846648e-05 * 0.046 / 0.00209150326797386,
                },
                'natural gas, low pressure': {
                    'amount': 4.814980720846648e-05 * 19.9481865284974 / 0.00209150326797386,
                },
                'potato starch': {
                    'amount': 4.814980720846648e-05 * 5.95 / 0.00209150326797386,
                },
                'Propane': {
                    'amount': 4.814980720846648e-05 * 0.000163 / 0.00209150326797386,
                },
                'Nitrogen oxides': {
                    'amount': 4.814980720846648e-05 * 0.03 / 0.00209150326797386
                }
            }
        for exc in ds['exchanges']:
            print(exc['name'])
            for key, value in expected[exc['name']].items():
                if isinstance(value, Number):
                    assert allclose(exc[key], value)
                else:
                    assert exc[key] == value
