# -*- coding: utf-8 -*-
from ocelot.errors import InvalidExchange
from ocelot.transformations.cutoff.combined import (
    add_exchanges,
    combined_production,
    combined_production_with_byproducts,
    combined_production_without_products,
    handle_split_dataset,
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

def test_add_exchanges():
    first = {'exchanges': [
        {'id': 1, 'amount': 1, 'type': 'reference product'},
        {'id': 2, 'amount': 2, 'type': 'byproduct'},
        {'id': 4, 'amount': 4, 'type': 'to environment'},
    ]}
    second = {'exchanges': [{
        'id': 1,
        'amount': 10,
        'type': 'reference product',  # Need to add production amounts too
    }, {
        'id': 2,
        'amount': 20,
        'type': 'byproduct'
    }, {
        'id': 3,  # 4 not in first, 3 not in second, but no error
        'amount': 30,
        'type': 'to environment'
    }]}
    expected = {'exchanges': [
        {
            'id': 1,
            'amount': 11,
            'type': 'reference product',
            'uncertainty': {
                'minimum': 11,
                'maximum': 11,
                'pedigree matrix': {},
                'standard deviation 95%': 0,
                'type': 'undefined'
            }
        },
        {'id': 2, 'amount': 22, 'type': 'byproduct'},
        {'id': 4, 'amount': 4, 'type': 'to environment'},
    ]}
    assert add_exchanges(first, second) == expected

def test_merge_byproducts_error():
    problem = [{
        'exchanges': [{
            'type': 'byproduct',
            'byproduct classification': 'allocatable product'
        }]
    }]
    with pytest.raises(InvalidExchange):
        merge_byproducts(problem)

def test_merge_byproducts():
    given = [{
        'name': 'first',
        'exchanges': [{
            'id': 1,
            'type': 'reference product',
            'name': 'first rp',
            'amount': 1
        }, {
            'id': 2,
            'type': 'to environment',
            'name': 'emission',
            'amount': 8
        }]
    }, {
        'name': 'second',
        'exchanges': [{
            'id': 3,
            'type': 'reference product',
            'name': 'second rp',
            'amount': 1
        }, {
            'id': 1,
            'type': 'to environment',
            'name': 'another emission',
            'amount': 100
        }]
    }, {
        'name': 'first',
        'exchanges': [{
            'id': 1,
            'type': 'reference product',
            'name': 'first rp',
            'amount': 1
        }, {
            'id': 2,
            'type': 'to environment',
            'name': 'emission',
            'amount': 2
        }]
    }]
    expected = [{
        'name': 'first',
        'exchanges': [{
            'id': 1,
            'type': 'reference product',
            'name': 'first rp',
            'amount': 2,
            'uncertainty': {
                'minimum': 2,
                'maximum': 2,
                'pedigree matrix': {},
                'standard deviation 95%': 0,
                'type': 'undefined'
            }
        }, {
            'id': 2,
            'type': 'to environment',
            'name': 'emission',
            'amount': 10
        }]
    }, {
        'name': 'second',
        'exchanges': [{
            'id': 3,
            'type': 'reference product',
            'name': 'second rp',
            'amount': 1
        }, {
            'id': 1,
            'type': 'to environment',
            'name': 'another emission',
            'amount': 100
        }]
    }]
    for obj in merge_byproducts(given):
        assert any(obj == ds for ds in expected)

@pytest.fixture(scope='function')
def no_combined_production(monkeypatch):
    monkeypatch.setattr(
        'ocelot.transformations.cutoff.combined.combined_production',
        lambda x: x
    )
    monkeypatch.setattr(
        'ocelot.transformations.cutoff.combined.economic_allocation',
        lambda x: [x]
    )

def test_combined_production_with_byproducts(no_combined_production):
    given = [{
        'name': 'first',
        'exchanges': [{
            'id': 1,
            'type': 'reference product',
            'name': 'first rp',
            'amount': 1
        }, {
            'id': 2,
            'type': 'to environment',
            'name': 'emission',
            'amount': 8
        }]
    }, {
        'name': 'first',
        'exchanges': [{
            'id': 1,
            'type': 'reference product',
            'name': 'first rp',
            'amount': 1
        }, {
            'id': 2,
            'type': 'to environment',
            'name': 'emission',
            'amount': 2
        }]
    }]
    expected = [{
        'name': 'first',
        'exchanges': [{
            'id': 1,
            'type': 'reference product',
            'name': 'first rp',
            'amount': 2,
            'uncertainty': {
                'minimum': 2,
                'maximum': 2,
                'pedigree matrix': {},
                'standard deviation 95%': 0,
                'type': 'undefined'
            }
        }, {
            'id': 2,
            'type': 'to environment',
            'name': 'emission',
            'amount': 10
        }]
    }]
    assert combined_production_with_byproducts(given) == expected

def test_handle_split_dataset(monkeypatch):
    monkeypatch.setattr(
        'ocelot.transformations.cutoff.combined.waste_treatment_allocation',
        lambda x: "waste treatment"
    )
    monkeypatch.setattr(
        'ocelot.transformations.cutoff.combined.recycling_allocation',
        lambda x: ("recycling", x)
    )
    given = {
        'exchanges': [{
            'type': 'reference product',
            'byproduct classification': 'waste'
        }]
    }
    assert handle_split_dataset(given) == 'waste treatment'
    given = {
        'name': 'up',
        'exchanges': [{
            'type': 'reference product',
            'byproduct classification': 'recyclable',
            'name': 'down'
        }]
    }
    label, ds = handle_split_dataset(given)
    assert label == 'recycling'
    assert ds['name'] == 'up, from down'

    error = {
        'exchanges': [{
            'type': 'reference product',
            'byproduct classification': 'nope',
        }]
    }
    with pytest.raises(InvalidExchange):
        handle_split_dataset(error)

def test_combined_production_without_products(monkeypatch):
    monkeypatch.setattr(
        'ocelot.transformations.cutoff.combined.combined_production',
        lambda x: x
    )
    monkeypatch.setattr(
        'ocelot.transformations.cutoff.combined.handle_split_dataset',
        lambda x: x
    )
    given = [[1, 2, 3], [4, 5, 6]]
    expected = [1, 2, 3, 4, 5, 6]
    assert combined_production_without_products(given) == expected
