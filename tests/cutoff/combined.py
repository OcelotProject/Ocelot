# -*- coding: utf-8 -*-
from ocelot.transformations.cutoff.combined import (
    add_exchanges,
    combined_production,
    combined_production_with_byproducts,
    merge_byproducts,
    nonzero_reference_product_exchanges,
    selected_product,
)
from copy import deepcopy
import pytest


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


@pytest.fixture(scope='function')
def no_recalculate(monkeypatch):
    monkeypatch.setattr(
        'ocelot.transformations.cutoff.combined.recalculate',
        lambda x: x
    )

def test_combined_production(no_recalculate):
    given = {'exchanges': [
        {
            'type': 'reference product',
            'amount': 2,
            'variable': "first",
        }, {
            'type': 'reference product',
            'amount': 3,
            'variable': 'second'
        },
        {'type': 'from technosphere'},
        {'type': 'to environment'}
    ]}
    expected = [{'exchanges': [
        {
            'type': 'reference product',
            'amount': 2,
            'variable': 'first',
            'uncertainty': {
                'minimum': 2,
                'maximum': 2,
                'pedigree matrix': {},
                'standard deviation 95%': 0,
                'type': 'undefined'
            }
        }, {
            'type': 'dropped product',
            'amount': 0,
            'variable': 'second',
            'uncertainty': {
                'minimum': 0,
                'maximum': 0,
                'pedigree matrix': {},
                'standard deviation 95%': 0,
                'type': 'undefined'
            }
        },
        {'type': 'from technosphere'},
        {'type': 'to environment'}
    ]}, {
        'exchanges': [{
            'type': 'reference product',
            'amount': 3,
            'variable': 'second',
            'uncertainty': {
                'minimum': 3,
                'maximum': 3,
                'pedigree matrix': {},
                'standard deviation 95%': 0,
                'type': 'undefined'
            }
        }, {
            'type': 'dropped product',
            'amount': 0,
            'variable': 'first',
            'uncertainty': {
                'minimum': 0,
                'maximum': 0,
                'pedigree matrix': {},
                'standard deviation 95%': 0,
                'type': 'undefined'
            }
        },
        {'type': 'from technosphere'},
        {'type': 'to environment'}
    ]}]
    original = deepcopy(given)
    assert combined_production(given) == expected
    assert original == given
