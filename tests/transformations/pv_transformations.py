# -*- coding: utf-8 -*-
from ocelot.transformations.production_volumes import add_pv_to_allocatable_byproducts


def test_add_pv_to_allocatable_byproducts():
    given = [{
        'name': '',
        'exchanges': [{
            'name': '',
            'amount': 3,
            'type': 'byproduct',
            'byproduct classification': 'allocatable product',
            'production volume': {'amount': 0}
        }, {
            'name': '',
            'amount': 6,
            'type': 'reference product',
            'production volume': {'amount': 10}
        }]
    }]
    expected = [{
        'name': '',
        'exchanges': [{
            'name': '',
            'amount': 3,
            'type': 'byproduct',
            'byproduct classification': 'allocatable product',
            'production volume': {'amount': 5}
        }, {
            'name': '',
            'amount': 6,
            'type': 'reference product',
            'production volume': {'amount': 10}
        }]
    }]
    assert add_pv_to_allocatable_byproducts(given) == expected

def test_add_pv_to_allocatable_byproducts_skip_existing():
    given = [{
        'name': '',
        'exchanges': [{
            'name': '',
            'amount': 3,
            'type': 'byproduct',
            'byproduct classification': 'allocatable product',
            'production volume': {'amount': 1.2}
        }, {
            'name': '',
            'amount': 6,
            'type': 'reference product',
            'production volume': {'amount': 10}
        }]
    }]
    expected = [{
        'name': '',
        'exchanges': [{
            'name': '',
            'amount': 3,
            'type': 'byproduct',
            'byproduct classification': 'allocatable product',
            'production volume': {'amount': 1.2}
        }, {
            'name': '',
            'amount': 6,
            'type': 'reference product',
            'production volume': {'amount': 10}
        }]
    }]
    assert add_pv_to_allocatable_byproducts(given) == expected

def test_add_pv_to_allocatable_byproducts_waste_treatment():
    given = [{
        'name': '',
        'exchanges': [{
            'name': '',
            'amount': 3,
            'type': 'byproduct',
            'byproduct classification': 'allocatable product',
            'production volume': {'amount': 0}
        }, {
            'name': '',
            'amount': -6,
            'type': 'reference product',
            'production volume': {'amount': 10}
        }]
    }]
    expected = [{
        'name': '',
        'exchanges': [{
            'name': '',
            'amount': 3,
            'type': 'byproduct',
            'byproduct classification': 'allocatable product',
            'production volume': {'amount': 5}
        }, {
            'name': '',
            'amount': -6,
            'type': 'reference product',
            'production volume': {'amount': 10}
        }]
    }]
    assert add_pv_to_allocatable_byproducts(given) == expected
