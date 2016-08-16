# -*- coding: utf-8 -*-
from ocelot.transformations.utils import *
from ocelot.errors import InvalidMultioutputDataset, ZeroProduction
import pytest


def test_allocatable_production():
    exchanges = [
        {'type': 'reference product'},
        {'type': 'not reference product'},
        {'type': 'byproduct', 'byproduct classification': 'allocatable'},
        {'type': 'byproduct', 'byproduct classification': 'cat'},
        {'type': 'byproduct', 'byproduct classification': 'allocatable'},
    ]
    dataset = {'exchanges': exchanges}
    for x, y in zip(allocatable_production(dataset), exchanges[0:5:2]):
        assert x == y
    assert len(list(allocatable_production(dataset))) == 3

def test_nonproduction_exchanges():
    exchanges = [
        {'type': 'reference product'},
        {'type': 'not reference product'},
        {'type': 'byproduct', 'byproduct classification': 'allocatable'},
        {'type': 'byproduct', 'byproduct classification': 'cat'},
        {'type': 'byproduct', 'byproduct classification': 'allocatable'},
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
            'byproduct classification': 'allocatable',
            'name': 'should be skipped'
        },
    ]}
    expected = {'type': 'reference product', 'name': 'sandwich'}
    assert get_single_reference_product(given) == expected

def test_single_reference_product_multiple():
    given = {'exchanges': [
        {
            'type': 'reference product',
            'name': 'sandwich'
        },
        {
            'type': 'reference product',
            'name': 'hamburger'
        },
    ]}
    with pytest.raises(InvalidMultioutputDataset):
        get_single_reference_product(given)

def test_single_reference_product_none():
    with pytest.raises(ValueError):
        get_single_reference_product({'exchanges': []})

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
    given = {'exchanges': [
        {
            'type': 'reference product',
            'amount': 0
        },
    ]}
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
    given = {'production volume': None}
    expected = {
        'type': 'dropped product',
        'amount': 0
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
        'production volume': None
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
        'amount': 0
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
        'byproduct classification': "allocatable",
        'amount': 42
    }, {
        'type': 'reference product',
        'amount': 20,
        'production volume': None
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
        'amount': 0
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
    given = {'exchanges': [{
        'type': 'reference product',
        'amount': 0
    }]}
    with pytest.raises(ZeroProduction):
        choose_reference_product_exchange(given, given['exchanges'][0])
