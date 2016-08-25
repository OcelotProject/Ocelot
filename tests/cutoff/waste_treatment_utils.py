# -*- coding: utf-8 -*-
from ocelot.transformations.cutoff.wastes import flip_non_allocatable_byproducts


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
            'formula': 'foo',
            'name': "Fix me!",
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
            'formula': '-1 * (foo)',
            'name': "Fix me!, Recycled Content cut-off",
        },
    ]}
    assert flip_non_allocatable_byproducts(given) == expected