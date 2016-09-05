# -*- coding: utf-8 -*-
from ocelot.errors import InvalidMultioutputDataset
from ocelot.transformations.cutoff.utils import (
    delete_allocation_method,
    flip_non_allocatable_byproducts,
)
import pytest


def test_delete_allocation_method():
    given = {'allocation method': 'something'}
    assert delete_allocation_method(given) == [{}]

    given = {'foo': 'bar'}
    assert delete_allocation_method(given) == [{'foo': 'bar'}]

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
