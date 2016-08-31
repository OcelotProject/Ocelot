# -*- coding: utf-8 -*-
from ocelot.errors import InvalidMultioutputDataset
from ocelot.transformations.cutoff.utils import (
    flip_non_allocatable_byproducts,
    label_reference_products,
)
import pytest


def test_flip_non_allocatable_byproducts():
    given = {
        'something else': 'woo!',
        'exchanges': [
        {
            'type': 'reference product',
            'amount': 1,
        },
        {
            'type': 'byproduct',
            'byproduct classification': 'allocatable product',
            'amount': 2,
        },
        {
            'type': 'byproduct',
            'byproduct classification': 'waste',
            'amount': 3,
        },
        {
            'type': 'byproduct',
            'byproduct classification': 'recyclable',
            'amount': 4,
            'formula': 'foo'
        },
    ]}
    expected = {
        'something else': 'woo!',
        'exchanges': [
        {
            'type': 'reference product',
            'amount': 1,
        },
        {
            'type': 'byproduct',
            'byproduct classification': 'allocatable product',
            'amount': 2,
        },
        {
            'type': 'from technosphere',
            'amount': -3,
        },
        {
            'type': 'from technosphere',
            'amount': -4,
            'formula': '-1 * (foo)'
        },
    ]}
    assert flip_non_allocatable_byproducts(given) == expected

def test_label_reference_products():
    valid = [{
        'type': 'transforming activity',
        'exchanges': [{
            'type': 'reference product',
            'name': 'foo'
        }]
    }]
    expected = [{
        'type': 'transforming activity',
        'reference product': 'foo',
        'exchanges': [{
            'type': 'reference product',
            'name': 'foo'
        }]
    }]
    assert label_reference_products(valid)

def test_label_reference_products_no_exchanges():
    invalid = [{
        'type': 'transforming activity',
        'exchanges': [{'type': 'nope'}]
    }]
    with pytest.raises(ValueError):
        label_reference_products(invalid)

def test_label_reference_products_multiple_rp():
    invalid = [{
        'type': 'transforming activity',
        'exchanges': [
            {'type': 'reference product'},
            {'type': 'reference product'},
        ]
    }]
    with pytest.raises(InvalidMultioutputDataset):
        label_reference_products(invalid)
