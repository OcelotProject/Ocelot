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
