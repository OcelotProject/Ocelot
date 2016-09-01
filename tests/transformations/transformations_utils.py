# -*- coding: utf-8 -*-
from ocelot.transformations.utils import *
from ocelot.errors import InvalidMultioutputDataset, ZeroProduction
import pytest


def test_allocatable_production():
    exchanges = [
        {'type': 'reference product'},
        {'type': 'not reference product'},
        {'type': 'byproduct', 'byproduct classification': 'allocatable product'},
        {'type': 'byproduct', 'byproduct classification': 'cat'},
        {'type': 'byproduct', 'byproduct classification': 'allocatable product'},
    ]
    dataset = {'exchanges': exchanges}
    for x, y in zip(allocatable_production(dataset), exchanges[0:5:2]):
        assert x == y
    assert len(list(allocatable_production(dataset))) == 3

def test_allocatable_production_include_all_reference_products():
    given = {"exchanges": [
        {'type': 'reference product', 'byproduct classification': 'recyclable'},
        {'type': 'reference product', 'byproduct classification': 'allocatable product'},
        {'type': 'reference product', 'byproduct classification': 'waste'},
        {'type': 'reference product', 'byproduct classification': 'foo'},
    ]}
    assert len(list(allocatable_production(given))) == 4

def test_nonproduction_exchanges():
    exchanges = [
        {'type': 'reference product'},
        {'type': 'not reference product'},
        {'type': 'byproduct', 'byproduct classification': 'allocatable product'},
        {'type': 'byproduct', 'byproduct classification': 'cat'},
        {'type': 'byproduct', 'byproduct classification': 'allocatable product'},
    ]
    dataset = {'exchanges': exchanges}
    for x, y in zip(nonproduction_exchanges(dataset), exchanges[1:4:2]):
        assert x == y
    assert len(list(nonproduction_exchanges(dataset))) == 2

def test_get_property_by_name():
    given = {'properties': [{'name': 'foo', 'amount': 42}]}
    assert get_property_by_name(given, "foo") == {'name': 'foo', 'amount': 42}

def test_get_property_by_name_not_present():
    given = {'properties': [{'name': 'bar', 'amount': 42}]}
    assert get_property_by_name({}, "foo") == {}

def test_get_numerical_property():
    given = {'properties': [{'name': 'foo', 'amount': 42}]}
    assert get_numerical_property(given, "foo") == 42

def test_get_numerical_property_no_properties():
    assert get_numerical_property({}, "foo") is None

def test_get_numerical_property_not_correct_property():
    given = {'properties': [{'name': 'foo', 'amount': 42}]}
    assert get_numerical_property(given, "bar") is None

def test_single_reference_product():
    given = {'exchanges': [
        {
            'type': 'reference product',
            'name': 'sandwich'
        },
        {
            'type': 'not reference product',
            'name': 'woooo!'
        },
        {
            'type': 'byproduct',
            'byproduct classification': 'allocatable product',
            'name': 'should be skipped'
        },
    ]}
    expected = {'type': 'reference product', 'name': 'sandwich'}
    assert get_single_reference_product(given) == expected

def test_single_reference_product_multiple():
    given = {
        'filepath': 'foo',
        'exchanges': [
            {
                'type': 'reference product',
                'name': 'sandwich'
            },
            {
                'type': 'reference product',
                'name': 'hamburger'
            },
        ]
    }
    with pytest.raises(InvalidMultioutputDataset):
        get_single_reference_product(given)

def test_single_reference_product_none():
    with pytest.raises(ValueError):
        get_single_reference_product({
            'filepath': 'foo',
            'exchanges': [{'type': 'something'}]
        })

def test_normalize_reference_production_amount():
    given = {'exchanges': [
        {
            'type': 'reference product',
            'amount': 0.5
        },
        {
            'type': 'something else',
            'amount': 10
        }
    ]}
    expected = {'exchanges': [
        {
            'type': 'reference product',
            'amount': 1
        },
        {
            'type': 'something else',
            'amount': 20
        }
    ]}
    assert normalize_reference_production_amount(given) == expected

def test_normalize_reference_production_amount_zero_amount():
    given = {
        'filepath': 'foo',
        'exchanges': [{
            'type': 'reference product',
            'amount': 0
        }]
    }
    with pytest.raises(ZeroProduction):
        normalize_reference_production_amount(given)

def test_activity_grouper():
    given = {
        'name': 'foo',
        'exchanges': []
    }
    assert activity_grouper(given) == ('foo', ())
    given = {
        'name': 'bar',
        'exchanges': [{
            'type': 'reference product',
            'name': 'b'
        }, {
            'type': 'reference product',
            'name': 'a'
        }]
    }
    assert activity_grouper(given) == ('bar', ('a', 'b'))

def test_label_reference_product():
    given = {'exchanges': [{
        'type': 'reference product',
        'name': 'foo'
    }]}
    assert label_reference_product(given)['reference product'] == 'foo'

def test_remove_uncertainty():
    expected = {
        'amount': 42,
        'uncertainty': {
        'minimum': 42,
            'maximum': 42,
            'pedigree matrix': {},
            'standard deviation 95%': 0,
            'type': 'undefined'
        }
    }
    assert remove_exchange_uncertainty({'amount': 42}) == expected

def test_nonreference_product():
    given = {
        'production volume': 'delete me',
        'formula': 'delete me too'
    }
    expected = {
        'type': 'dropped product',
        'amount': 0,
        'uncertainty': {
            'minimum': 0,
            'maximum': 0,
            'pedigree matrix': {},
            'standard deviation 95%': 0,
            'type': 'undefined'
        }
    }
    assert nonreference_product(given) == expected


@pytest.fixture(scope="function")
def no_normalization(monkeypatch):
    monkeypatch.setattr(
        'ocelot.transformations.utils.normalize_reference_production_amount',
        lambda x: x
    )

def test_choose_reference_product_exchange(no_normalization):
    given = {'exchanges': [{
        'type': 'reference product',
        'amount': 42
    }, {
        'type': 'reference product',
        'amount': 20,
        'formula': 'delete me',
        'production volume': 'delete me too',
    }, {
        'type': 'other thing',
        'amount': 100
    }]}
    expected = {'exchanges': [{
        'amount': 42,
        'type': 'reference product',
        'uncertainty': {
            'minimum': 42,
            'maximum': 42,
            'pedigree matrix': {},
            'standard deviation 95%': 0,
            'type': 'undefined'
        }
    }, {
        'type': 'dropped product',
        'amount': 0,
        'uncertainty': {
            'minimum': 0,
            'maximum': 0,
            'pedigree matrix': {},
            'standard deviation 95%': 0,
            'type': 'undefined'
        }
    }, {
        'type': 'other thing',
        'amount': 10
    }]}
    answer = choose_reference_product_exchange(given, given['exchanges'][0], 0.1)
    assert answer == expected
    for one, two in zip(given['exchanges'], answer['exchanges']):
        # Check for copy
        assert one is not two

def test_choose_reference_product_exchange_byproducts(no_normalization):
    given = {'exchanges': [{
        'type': 'byproduct',
        'byproduct classification': "allocatable product",
        'amount': 42
    }, {
        'type': 'reference product',
        'amount': 20,
        'production volume': 'delete me',
        'formula': 'delete me too',
    }, {
        'type': 'other thing',
        'amount': 100
    }]}
    expected = {'exchanges': [{
        'amount': 42,
        'type': 'reference product',
        'uncertainty': {
            'minimum': 42,
            'maximum': 42,
            'pedigree matrix': {},
            'standard deviation 95%': 0,
            'type': 'undefined'
        }
    }, {
        'type': 'dropped product',
        'amount': 0,
        'uncertainty': {
            'minimum': 0,
            'maximum': 0,
            'pedigree matrix': {},
            'standard deviation 95%': 0,
            'type': 'undefined'
        }
    }, {
        'type': 'other thing',
        'amount': 10
    }]}
    answer = choose_reference_product_exchange(given, given['exchanges'][0], 0.1)
    assert answer == expected
    for one, two in zip(given['exchanges'], answer['exchanges']):
        # Check for copy
        assert one is not two

def test_choose_reference_product_exchange_zero_production(no_normalization):
    given = {
        'filepath': 'foo',
        'exchanges': [{
            'type': 'reference product',
            'amount': 0
        }]
    }
    with pytest.raises(ZeroProduction):
        choose_reference_product_exchange(given, given['exchanges'][0])

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

def test_activity_hash():
    given = {
        'name': 'a',
        'reference product': 'b',
        'unit': 'c',
        'location': 'd',
        'start date': 'e',
        'end date': 'f',
        'foo': 'bar',
    }
    assert activity_hash({})
    assert activity_hash(given)
