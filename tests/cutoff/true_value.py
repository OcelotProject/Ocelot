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

def test_true_value_allocation_factors(no_allocation):
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

def test_normal_true_value_allocation():
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
            'amount': 4
        }, {
            'name': 'true value relation',
            'amount': 7.5
        }]
    }, {
        'name': 'third',
        'type': 'reference product',
        'amount': 10,
        'properties': [{
            'name': 'price',
            'amount': 5
        }, {
            'name': 'true value relation',
            'amount': 2.5
        }]
    }, {
        'name': 'fourth',
        'type': 'biosphere',
        'amount': 100
    }]}
    # Total revenue is 100, of which 90 has true value
    # Total true value is 100, of which 75 comes from ``second``
    get_biosphere_exchange = lambda x: [exc for exc in x['exchanges'] if exc['name'] == 'fourth'][0]
    for ds in economic_allocation(dataset):
        assert len(ds['exchanges']) == 4
        assert sum(1 for exc in ds['exchanges'] if exc['type'] == 'dropped product') == 2
        assert sum(1 for exc in ds['exchanges'] if exc['amount'] == 0) == 2
        rp = get_single_reference_product(ds)
        bio_exchange = get_biosphere_exchange(ds)
        assert rp['type'] == 'reference product'
        assert rp['amount'] == 1
        if rp['name'] == 'first':
            assert bio_exchange['amount'] == 100 / 4 * (4 * 2.5 / 100)
        elif rp['name'] == 'second':
            assert bio_exchange['amount'] == (7.5 * 10) / (7.5 * 10 + 2.5 * 10) * 90 / 100 * 100 / 10
        else:
            assert bio_exchange['amount'] == (2.5 * 10) / (7.5 * 10 + 2.5 * 10) * 90 / 100 * 100 / 10


### Test real test data

@pytest.fixture(scope="module")
def cogen():
    fp = os.path.join(os.path.dirname(__file__), "..", "data",
                      "heat-cogeneration-glo.spold")
    return generic_extractor(fp)[0]

def test_load_validate_cogeneration_dataset(cogen):
    assert dataset_schema(cogen)

def test_choice_allocation_method(cogen):
    assert choose_allocation_method(cogen) == economic_allocation

def test_allocation_function_output_valid(cogen):
    for new_ds in economic_allocation(cogen):
        assert dataset_schema(new_ds)

def test_allocate_cogeneration_dataset(cogen):
    """Cogeneration dataset produces:

    1. heat, district or industrial, natural gas
        * Reference product
        * Price: 0.0106 €/MJ
        * True value: 0.184213553594 €/MJ
        * Amount: 4.1 MJ
        * Revenue: 0.04346 €
        * True value revenue: 0.7552755697353999 €
    2. electricity, high voltage
        * Allocatable byproduct
        * Price: 0.0977 €/kWh
        * True value: 3.6 €/kWh
        * Amount: 1 kWh
        * Revenue: 0.0977 €
        * True value revenue: 3.6 €

    Allocation factors: 0.3078775857183338, 0.6921224142816661
    TV allocation factors: 0.17341625291951063, 0.8265837470804893

    Elementary exchange: 0.622135922330097 kg Carbon dioxide, fossil
    Input: 6.47766990291262E-10 unit gas power plant, 100MW electrical
    Input: 0.298730395817774 m3 natural gas, high pressure

    This real world dataset does not test for a mix of true-value and non-true-value exchanges, but this is tested in the artificial test cases above.

    """
    datasets = economic_allocation(cogen)
    assert len(datasets) == 2

    for ds in datasets:
        assert len(ds['exchanges']) == 5
        for key, value in cogen.items():
            if key == 'exchanges':
                continue
            else:
                assert ds[key] == value

        rp = get_single_reference_product(ds)
        if rp['name'] == 'heat, district or industrial, natural gas':
            expected = {
                'heat, district or industrial, natural gas': {
                    'amount': 1,
                    'type': 'reference product',
                },
                'electricity, high voltage': {
                    'amount': 0,
                    'type': 'dropped product',
                },
                'Carbon dioxide, fossil': {
                    'amount': 0.17341625291951063 * 0.622135922330097 / 4.1,
                },
                'gas power plant, 100MW electrical': {
                    'amount': 0.17341625291951063 * 6.47766990291262E-10 / 4.1,
                },
                'natural gas, high pressure': {
                    'amount': 0.17341625291951063 * 0.298730395817774 / 4.1,
                },
            }
        else:
            expected = {
                'heat, district or industrial, natural gas': {
                    'amount': 0,
                    'type': 'dropped product',
                },
                'electricity, high voltage': {
                    'amount': 1,
                    'type': 'reference product',
                },
                'Carbon dioxide, fossil': {
                    'amount': 0.8265837470804893 * 0.622135922330097,
                },
                'gas power plant, 100MW electrical': {
                    'amount': 0.8265837470804893 * 6.47766990291262E-10,
                },
                'natural gas, high pressure': {
                    'amount': 0.8265837470804893 * 0.298730395817774,
                },
            }
        for exc in ds['exchanges']:
            print(exc['name'])
            for key, value in expected[exc['name']].items():
                if isinstance(value, Number):
                    assert allclose(exc[key], value)
                else:
                    assert exc[key] == value
