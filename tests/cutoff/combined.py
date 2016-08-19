# -*- coding: utf-8 -*-
from ocelot.transformations.cutoff.combined import (
    nonzero_reference_product_exchanges,
    selected_product,
)


def test_nonzero_reference_product_exchanges():
    given = {'exchanges': [{
        'type': 'reference product',
        'name': 1,
        'amount': 1
    }, {
        'type': 'reference product',
        'name': 2,
        'amount': 0
    }, {
        'type': 'reference product',
        'name': 3,
        'amount': 1
    }, {
        'type': 'non-reference product',
        'name': 4,
        'amount': 1
    }, {
        'type': 'reference product',
        'name': 5,
        'amount': 1
    }]}
    assert [x['name'] for x in nonzero_reference_product_exchanges(given)] == [1,3,5]

def test_selected_product():
    given = {'formula': 'delete me', 'amount': 42}
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
    assert selected_product(given) == expected
