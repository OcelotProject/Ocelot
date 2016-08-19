# -*- coding: utf-8 -*-
from ocelot.transformations.cutoff.combined import (
    nonzero_reference_product_exchanges,
    selected_product,
)


def test_nonzero_reference_product_exchanges():
    pass

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
