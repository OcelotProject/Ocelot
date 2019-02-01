# -*- coding: utf-8 -*-
from ocelot.errors import MultipleGlobalDatasets
from ocelot.transformations.locations import (
    drop_zero_pv_row_datasets,
    relabel_global_to_row,
)
from copy import deepcopy
import pytest


def test_relabel_global_to_row():
    given = [{
        'name': 'make something',
        'location': 'GLO',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'unit': '',
            'type': 'reference product',
            'production volume': {'amount': 0},
            'amount': 1,
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'unit': '',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'unit': '',
            'type': 'reference product',
            'amount': 1,
            'production volume': {'amount': 0}
        }]
    }, {
        'name': 'make something else',
        'location': 'GLO',
        'unit': '',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume': {'amount': 0}
        }]
    }, {
        'name': 'make something else',
        'location': 'somewhere else',
        'unit': '',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume': {'amount': 0}
        }]
    }]
    expected = [{
        'name': 'make something',
        'location': 'RoW',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'unit': '',
            'type': 'reference product',
            'amount': 1,
            'production volume': {'amount': 0}
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'unit': '',
            'type': 'reference product',
            'amount': 1,
            'production volume': {'amount': 0}
        }]
    }, {
        'name': 'make something else',
        'location': 'RoW',
        'type': 'market activity',
        'exchanges': [{
            'name': 'another product',
            'unit': '',
            'type': 'reference product',
            'amount': 1,
            'production volume': {'amount': 0}
        }]
    }, {
        'name': 'make something else',
        'location': 'somewhere else',
        'type': 'market activity',
        'exchanges': [{
            'name': 'another product',
            'unit': '',
            'type': 'reference product',
            'amount': 1,
            'production volume': {'amount': 0}
        }]
    }]
    # Can't directly compare dictionaries if order has changed
    hashify = lambda x: {(y['name'], y['location']) for y in x}
    assert hashify(relabel_global_to_row(given)) == hashify(expected)

def test_relabel_global_to_row_dropped_products():
    given = [{
        'name': 'make something',
        'location': 'GLO',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'unit': '',
            'type': 'reference product',
            'production volume': {'amount': 0},
            'amount': 1,
        }, {
            'name': 'another product',
            'unit': '',
            'type': 'byproduct',
            'byproduct classification': 'allocatable product',
            'production volume': {'amount': 0},
            'amount': 1,
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'unit': '',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'unit': '',
            'type': 'reference product',
            'amount': 1,
            'production volume': {'amount': 0}
        }]
    }]
    expected = [{
        'name': 'make something',
        'location': 'RoW',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'unit': '',
            'type': 'reference product',
            'amount': 1,
            'production volume': {'amount': 0}
        }, {
            'name': 'another product',
            'unit': '',
            'type': 'byproduct',
            'byproduct classification': 'allocatable product',
            'production volume': {'amount': 0},
            'amount': 0,
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'unit': '',
            'type': 'reference product',
            'amount': 1,
            'production volume': {'amount': 0}
        }]
    }]
    # Can't directly compare dictionaries if order has changed
    hashify = lambda x: {(y['name'], y['location']) for y in x}
    assert hashify(relabel_global_to_row(given)) != hashify(expected)

def test_relabel_global_to_row_ignore_zero_dropped_products():
    given = [{
        'name': 'make something',
        'location': 'GLO',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'unit': '',
            'type': 'reference product',
            'production volume': {'amount': 0},
            'amount': 1,
        }, {
            'name': 'another product',
            'unit': '',
            'type': 'byproduct',
            'byproduct classification': 'allocatable product',
            'production volume': {'amount': 0},
            'amount': 0,
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'unit': '',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'unit': '',
            'type': 'reference product',
            'amount': 1,
            'production volume': {'amount': 0}
        }]
    }]
    expected = [{
        'name': 'make something',
        'location': 'RoW',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'unit': '',
            'type': 'reference product',
            'amount': 1,
            'production volume': {'amount': 0}
        }, {
            'name': 'another product',
            'unit': '',
            'type': 'byproduct',
            'byproduct classification': 'allocatable product',
            'production volume': {'amount': 0},
            'amount': 0,
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'unit': '',
            'type': 'reference product',
            'amount': 1,
            'production volume': {'amount': 0}
        }]
    }]
    # Can't directly compare dictionaries if order has changed
    hashify = lambda x: {(y['name'], y['location']) for y in x}
    assert hashify(relabel_global_to_row(given)) == hashify(expected)


def test_relabel_global_to_row_skip_market_groups():
    given = [{
        'name': 'shellfish',
        'type': 'market group',
        'location': 'GLO',
        'exchanges': [{
            'name': 'a product',
            'amount': 1,
            'type': 'reference product'
        }]
    }, {
        'name': 'shellfish',
        'type': 'market group',
        'location': 'CN',
        'exchanges': [{
            'name': 'a product',
            'amount': 1,
            'type': 'reference product'
        }]
    }]
    expected = deepcopy(given)
    assert relabel_global_to_row(given) == expected

def test_relabel_global_to_row_only_single_global():
    given = [{
        'name': 'make something',
        'type': 'market activity',
        'location': 'GLO',
        'exchanges': [{
            'name': 'a product',
            'amount': 1,
            'type': 'reference product'
        }]
    }]
    expected = deepcopy(given)
    assert relabel_global_to_row(given) == expected

def test_relabel_global_to_row_only_single_nonglobal():
    given = [{
        'name': 'make something',
        'type': 'market activity',
        'location': 'somewhere',
        'exchanges': [{
            'name': 'a product',
            'amount': 1,
            'type': 'reference product'
        }]
    }]
    expected = deepcopy(given)
    assert relabel_global_to_row(given) == expected

def test_multiple_global_datasets():
    given = [{
        'name': 'make something',
        'type': 'market activity',
        'location': 'GLO',
        'exchanges': [{
            'name': 'a product',
            'amount': 1,
            'type': 'reference product'
        }]
    }, {
        'name': 'make something',
        'type': 'market activity',
        'location': 'GLO',
        'exchanges': [{
            'name': 'a product',
            'amount': 1,
            'type': 'reference product'
        }]
    }]
    with pytest.raises(MultipleGlobalDatasets):
        relabel_global_to_row(given)

def test_drop_zero_pv_row_datasets():
    data = [
        {
            'type': 'party activity',
            'location': 'RoW',
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 0}
            }]
        },
        {
            'type': 'market activity',
            'location': 'RoW',
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 10}
            }]
        },
        {
            'type': 'market activity',
            'location': 'Nowhere',
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 0}
            }]
        },
        {
            'type': 'market activity',
            'name': 'foo',
            'location': 'RoW',
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 0},
                'name': 'bar'
            }]
        },
    ]
    expected = [
        {
            'type': 'party activity',
            'location': 'RoW',
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 0}
            }]
        },
        {
            'type': 'market activity',
            'location': 'RoW',
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 10}
            }]
        },
        {
            'type': 'market activity',
            'location': 'Nowhere',
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 0}
            }]
        },
    ]
    assert drop_zero_pv_row_datasets(data) == expected


def test_relabel_global_to_row_subtract_pv():
    given = [{
        'name': 'make something',
        'location': 'GLO',
        'unit': '',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':100
            }
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'unit': '',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':10
            }
        }]
    }, {
        'name': 'make something else',
        'location': 'GLO',
        'unit': '',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':100
            }
        }]
    }, {
        'name': 'make something else',
        'location': 'somewhere else',
        'unit': '',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':50
            }
        }]
    }]
    expected = [{
        'name': 'make something',
        'location': 'RoW',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':90
            }
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':10
            }
        }]
    }, {
        'name': 'make something else',
        'location': 'RoW',
        'type': 'market activity',
        'exchanges': [{
            'name': 'another product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':50
            }
        }]
    }, {
        'name': 'make something else',
        'location': 'somewhere else',
        'type': 'market activity',
        'exchanges': [{
            'name': 'another product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':50
            }
        }]
    }]
    # Can't directly compare dictionaries if order has changed
    hashify = lambda x: {(y['name'], y['location'], y['exchanges'][0]['production volume']['amount']) for y in x}
    assert hashify(relabel_global_to_row(given)) == hashify(expected)

def test_relabel_global_to_row_subtract_origianal_pv():
    given = [{
        'name': 'make something',
        'location': 'GLO',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':100
            }
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'unit': '',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':10,
                'subtracted activity link volume': 40,
                'original amount': 50
            }
        }]
    }]
    expected = {
        'name': 'make something',
        'location': 'RoW',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':50,
                'global amount': 100,
            }
        }]
    }
    assert next(o for o in relabel_global_to_row(given) if o['location'] == 'RoW') == expected

def test_relabel_global_to_row_subtract_pv_overspecified_regional_pv():
    given = [{
        'name': 'make something',
        'location': 'GLO',
        'unit': '',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':100
            }
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'unit': '',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':110
            }
        }]
    }, {
        'name': 'make something else',
        'location': 'GLO',
        'unit': '',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':100
            }
        }]
    }, {
        'name': 'make something else',
        'location': 'somewhere else',
        'unit': '',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':150
            }
        }]
    }]
    expected = [{
        'name': 'make something',
        'location': 'RoW',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':0
            }
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'type': 'market activity',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':110
            }
        }]
    }, {
        'name': 'make something else',
        'location': 'RoW',
        'type': 'market activity',
        'exchanges': [{
            'name': 'another product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':0
            }
        }]
    }, {
        'name': 'make something else',
        'location': 'somewhere else',
        'type': 'market activity',
        'exchanges': [{
            'name': 'another product',
            'type': 'reference product',
            'unit': '',
            'amount': 1,
            'production volume':{
                'amount':150
            }
        }]
    }]
    # Can't directly compare dictionaries if order has changed
    hashify = lambda x: {(y['name'], y['location'], y['exchanges'][0]['production volume']['amount']) for y in x}
    assert hashify(relabel_global_to_row(given)) == hashify(expected)
