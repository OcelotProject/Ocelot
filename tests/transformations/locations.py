# -*- coding: utf-8 -*-
from ocelot.errors import MultipleGlobalDatasets
from ocelot.transformations.locations import (
    check_single_global_dataset,
    relabel_global_to_row,
    Topology,
)
from copy import deepcopy
import pytest


def test_relabel_global_to_row():
    given = [{
        'name': 'make something',
        'location': 'GLO',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product'
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product'
        }]
    }, {
        'name': 'make something else',
        'location': 'GLO',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product'
        }]
    }, {
        'name': 'make something else',
        'location': 'somewhere else',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product'
        }]
    }]
    expected = [{
        'name': 'make something',
        'location': 'RoW',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product'
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product'
        }]
    }, {
        'name': 'make something else',
        'location': 'RoW',
        'exchanges': [{
            'name': 'another product',
            'type': 'reference product'
        }]
    }, {
        'name': 'make something else',
        'location': 'somewhere else',
        'exchanges': [{
            'name': 'another product',
            'type': 'reference product'
        }]
    }]
    # Can't directly compare dictionaries if order has changed
    hashify = lambda x: {(y['name'], y['location']) for y in x}
    assert hashify(relabel_global_to_row(given)) == hashify(expected)

def test_relabel_global_to_row_only_single_global():
    given = [{
        'name': 'make something',
        'location': 'GLO',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product'
        }]
    }]
    expected = deepcopy(given)
    assert relabel_global_to_row(given) == expected

def test_relabel_global_to_row_only_single_nonglobal():
    given = [{
        'name': 'make something',
        'location': 'somewhere',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product'
        }]
    }]
    expected = deepcopy(given)
    assert relabel_global_to_row(given) == expected

def test_multiple_global_datasets():
    given = [{
        'name': 'make something',
        'location': 'GLO',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product'
        }]
    }, {
        'name': 'make something',
        'location': 'GLO',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product'
        }]
    }]
    with pytest.raises(MultipleGlobalDatasets):
        relabel_global_to_row(given)

@pytest.fixture(scope="module")
def topo():
    return Topology()

def test_topology_loading(topo):
    assert len(topo.data) > 400

def test_topology_contained(topo):
    assert topo.contained('RU') == {'Russia (Asia)', 'Russia (Europe)'}
    assert topo.contained('GLO') is None
    # Test compatibility labels
    assert topo.contained('IAI Area 8')
    with pytest.raises(KeyError):
        topo.contained('foo')

def test_topology_intersects(topo):
    assert 'UN-EUROPE' in topo.intersects('DE')
    assert 'RER w/o AT+BE+CH+DE+FR+IT' not in topo.intersects('CH')
    assert topo.intersects('GLO') is None
    # Test compatibility labels
    assert topo.intersects('IAI Area 8')
    with pytest.raises(KeyError):
        topo.intersects('foo')
