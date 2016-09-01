# -*- coding: utf-8 -*-
from ocelot.transformations.cutoff.allocation import *
import pytest


NO_ALLOCATION = {
    'type': 'transforming activity',
    'exchanges': [
        {'type': 'reference product', 'amount': 1},
    ]
}

MARKET_GROUP = {
    'type': 'market group',
    'exchanges': [
        {'type': 'reference product', 'amount': 1},
        {'type': 'reference product', 'amount': 1},
    ]
}

MARKET_ACTIVITY = {
    'type': 'market activity',
    'exchanges': [
        {'type': 'reference product', 'amount': 1},
        {'type': 'reference product', 'amount': 1},
    ]
}

CONSTRAINED_MARKET = {
    'type': 'market activity',
    'exchanges': [
        {
            'type': 'reference product',
            'amount': 1,
            'conditional exchange': True
        },
        {'type': 'reference product', 'amount': 1},
    ]
}

ECONOMIC = {
    'type': 'transforming activity',
    'exchanges': [
        {'type': 'reference product', 'amount': 1},
        {
            'type': 'byproduct',
            'amount': 1,
            'byproduct classification': 'allocatable product'},
    ]
}

WASTE = {
    'type': 'transforming activity',
    'exchanges': [
        {
            'type': 'reference product',
            'amount': -1,
            'byproduct classification': 'waste',
        }, {
            'type': 'byproduct',
            'amount': 1,
            'byproduct classification': 'allocatable product'},
    ]
}

RECYCLING = {
    'type': 'transforming activity',
    'exchanges': [
        {
            'type': 'reference product',
            'amount': -1,
            'byproduct classification': 'recyclable',
        }, {
            'type': 'byproduct',
            'amount': 1,
            'byproduct classification': 'allocatable product'},
    ]
}

COMBINED = {
    'type': 'transforming activity',
    'exchanges': [
        {
            'type': 'reference product',
            'amount': 1,
            'byproduct classification': 'waste'
        },
        {
            'type': 'reference product',
            'amount': 1,
            'byproduct classification': 'allocatable product'
        },
    ]
}

COMBINED_WITHOUT_PRODUCTS = {
    'type': 'transforming activity',
    'exchanges': [
        {
            'type': 'reference product',
            'amount': 1,
            'byproduct classification': 'waste'
        },
        {
            'type': 'reference product',
            'amount': 1,
            'byproduct classification': 'recyclable'
        },
    ]
}

COMBINED_WITH_BYPRODUCTS = {
    'type': 'transforming activity',
    'exchanges': [
        {
            'type': 'reference product',
            'amount': 1,
            'byproduct classification': 'waste'
        },
        {
            'type': 'reference product',
            'amount': 1,
            'byproduct classification': 'allocatable product'
        },
        {
            'type': 'byproduct',
            'amount': 1,
            'byproduct classification': 'allocatable product'
        },
    ]
}

def test_allocation_choice():
    assert choose_allocation_method(NO_ALLOCATION) is None
    assert choose_allocation_method(MARKET_GROUP) is None
    assert choose_allocation_method(MARKET_ACTIVITY) is None
    assert choose_allocation_method(CONSTRAINED_MARKET) == 'constrained market'
    assert choose_allocation_method(COMBINED) == 'combined production'
    assert choose_allocation_method(COMBINED_WITH_BYPRODUCTS) == 'combined production with byproducts'
    assert choose_allocation_method(COMBINED_WITHOUT_PRODUCTS) == 'combined production without products'
    assert choose_allocation_method(WASTE) == 'waste treatment'
    assert choose_allocation_method(RECYCLING) == 'recycling'
    assert choose_allocation_method(ECONOMIC) == 'economic'

def test_label_allocation_method():
    ds = label_allocation_method([ECONOMIC])
    assert ds[0]['allocation method'] == 'economic'

def test_no_allocation():
    given = {
        'exchanges': [{
            'type': 'reference product',
            'amount': 1
        }]
    }
    assert no_allocation(given) == [given]

def test_create_allocation_filter():
    func = create_allocation_filter("foo")
    assert func({'allocation method': 'foo'})
    assert not func({'allocation method': 'bar'})
