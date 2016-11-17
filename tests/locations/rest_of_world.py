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
        'exchanges': [{
            'name': 'a product',
            'unit': '',
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'unit': '',
        'exchanges': [{
            'name': 'a product',
            'unit': '',
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }, {
        'name': 'make something else',
        'location': 'GLO',
        'unit': '',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'production volume': {'amount': 0}
        }]
    }, {
        'name': 'make something else',
        'location': 'somewhere else',
        'unit': '',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'production volume': {'amount': 0}
        }]
    }]
    expected = [{
        'name': 'make something',
        'location': 'RoW',
        'exchanges': [{
            'name': 'a product',
            'unit': '',
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'exchanges': [{
            'name': 'a product',
            'unit': '',
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }, {
        'name': 'make something else',
        'location': 'RoW',
        'exchanges': [{
            'name': 'another product',
            'unit': '',
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }, {
        'name': 'make something else',
        'location': 'somewhere else',
        'exchanges': [{
            'name': 'another product',
            'unit': '',
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }]
    # Can't directly compare dictionaries if order has changed
    hashify = lambda x: {(y['name'], y['location']) for y in x}
    assert hashify(relabel_global_to_row(given)) == hashify(expected)

def test_relabel_global_to_row_skip_market_groups():
    given = [{
        'name': 'market group for foo',
        'location': 'GLO',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product'
        }]
    }, {
        'name': 'market group for foo',
        'location': 'CN',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product'
        }]
    }]
    expected = deepcopy(given)
    assert relabel_global_to_row(given) == expected

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
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'production volume':{
                'amount':100
            }
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'unit': '',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'production volume':{
                'amount':10
            }
        }]
    }, {
        'name': 'make something else',
        'location': 'GLO',
        'unit': '',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'production volume':{
                'amount':100
            }
        }]
    }, {
        'name': 'make something else',
        'location': 'somewhere else',
        'unit': '',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'production volume':{
                'amount':50
            }
        }]
    }]
    expected = [{
        'name': 'make something',
        'location': 'RoW',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'production volume':{
                'amount':90
            }
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'production volume':{
                'amount':10
            }
        }]
    }, {
        'name': 'make something else',
        'location': 'RoW',
        'exchanges': [{
            'name': 'another product',
            'type': 'reference product',
            'unit': '',
            'production volume':{
                'amount':50
            }
        }]
    }, {
        'name': 'make something else',
        'location': 'somewhere else',
        'exchanges': [{
            'name': 'another product',
            'type': 'reference product',
            'unit': '',
            'production volume':{
                'amount':50
            }
        }]
    }]
    # Can't directly compare dictionaries if order has changed
    hashify = lambda x: {(y['name'], y['location'], y['exchanges'][0]['production volume']['amount']) for y in x}
    assert hashify(relabel_global_to_row(given)) == hashify(expected)

def test_relabel_global_to_row_subtract_pv_overspecified_regional_pv():
    given = [{
        'name': 'make something',
        'location': 'GLO',
        'unit': '',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'production volume':{
                'amount':100
            }
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'unit': '',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'production volume':{
                'amount':110
            }
        }]
    }, {
        'name': 'make something else',
        'location': 'GLO',
        'unit': '',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'production volume':{
                'amount':100
            }
        }]
    }, {
        'name': 'make something else',
        'location': 'somewhere else',
        'unit': '',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'production volume':{
                'amount':150
            }
        }]
    }]
    expected = [{
        'name': 'make something',
        'location': 'RoW',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'production volume':{
                'amount':0
            }
        }]
    }, {
        'name': 'make something',
        'location': 'somewhere else',
        'exchanges': [{
            'name': 'a product',
            'type': 'reference product',
            'unit': '',
            'production volume':{
                'amount':110
            }
        }]
    }, {
        'name': 'make something else',
        'location': 'RoW',
        'exchanges': [{
            'name': 'another product',
            'type': 'reference product',
            'unit': '',
            'production volume':{
                'amount':0
            }
        }]
    }, {
        'name': 'make something else',
        'location': 'somewhere else',
        'exchanges': [{
            'name': 'another product',
            'type': 'reference product',
            'unit': '',
            'production volume':{
                'amount':150
            }
        }]
    }]
    # Can't directly compare dictionaries if order has changed
    hashify = lambda x: {(y['name'], y['location'], y['exchanges'][0]['production volume']['amount']) for y in x}
    assert hashify(relabel_global_to_row(given)) == hashify(expected)
