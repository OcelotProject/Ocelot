# -*- coding: utf-8 -*-
from ocelot.transformations import ensure_all_datasets_have_production_volume
from ocelot.transformations.cleanup import (
    deparameterize,
    mark_zero_pv_datasets,
    purge_zero_pv_datasets,
)
from ocelot.transformations.validation import (
    ensure_markets_only_have_one_reference_product,
    ensure_markets_dont_consume_their_ref_product,
)
import pytest


def test_ensure_all_datasets_have_production_volume_pass():
    data = [
        {
            'location': 'RoW',
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 10}
            }]
        },
    ]
    assert ensure_all_datasets_have_production_volume(data)

def test_ensure_all_datasets_have_production_volume_fail():
    data = [
        {
            'exchanges': [{
                'type': 'something else',
                'production volume': {'amount': 10}
            }]
        },
    ]
    with pytest.raises(AssertionError):
        ensure_all_datasets_have_production_volume(data)

def test_deparameterize():
    given = {
        'parameters': [
            {'formula': 'yes'},
            {'variable': 'no'}
        ],
        'exchanges': [{
            'formula': 'peter',
            'variable': 'paul',
            'production volume': {
                'variable': 'red',
                'formula': 'green',
                'key': 'value'
            },
            'properties': [
                {'formula': 'up', 'other': 'stuff'},
                {'variable': 'down', 'help': 'me'}
            ]
        }]
    }
    expected = {
        'parameters': [],
        'exchanges': [{'production volume': {'key': 'value'}}]
    }
    assert deparameterize(given) == expected

def test_purge_zero_pv_datasets():
    given = [{
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 0},
            }]
    }, {
            'zero pv': True,
            'name': '',
            'reference product': '',
            'location': '',
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 10},
            }]
    }]
    expected = [{
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 0},
        }]
    }]
    assert purge_zero_pv_datasets(given) == expected

def test_mark_zero_pv_datasets():
    given = [{
        'reference product': 'foo',
        'type': 'transforming activity',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }, {
        'reference product': 'foo',
        'type': 'market activity',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }, {
        'reference product': 'foo',
        'type': 'transforming activity',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 10}
        }]
    }]
    expected = [{
        'reference product': 'foo',
        'zero pv': True,
        'type': 'transforming activity',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }, {
        'reference product': 'foo',
        'type': 'market activity',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }, {
        'reference product': 'foo',
        'type': 'transforming activity',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 10}
        }]
    }]
    assert mark_zero_pv_datasets(given) == expected

def test_mark_zero_pv_datasets_row():
    given = [{
        'reference product': 'foo',
        'type': 'transforming activity',
        'location': 'somewhere',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }, {
        'reference product': 'foo',
        'type': 'transforming activity',
        'location': 'RoW',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }]
    expected = [{
        'reference product': 'foo',
        'type': 'transforming activity',
        'location': 'somewhere',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }, {
        'reference product': 'foo',
        'type': 'transforming activity',
        'zero pv': True,
        'location': 'RoW',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }]
    assert mark_zero_pv_datasets(given) == expected

def test_mark_zero_pv_datasets_skip_only_one():
    given = [{
        'reference product': 'foo',
        'type': 'transforming activity',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }]
    expected = [{
        'type': 'transforming activity',
        'reference product': 'foo',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }]
    assert mark_zero_pv_datasets(given) == expected

def test_mark_zero_pv_datasets_kind():
    given = [{
        'reference product': 'foo',
        'type': 'market activity',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }, {
        'reference product': 'foo',
        'type': 'other',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }, {
        'reference product': 'foo',
        'type': 'market activity',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 10}
        }]
    }]
    expected = [{
        'reference product': 'foo',
        'zero pv': True,
        'type': 'market activity',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }, {
        'reference product': 'foo',
        'type': 'other',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 0}
        }]
    }, {
        'reference product': 'foo',
        'type': 'market activity',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 10}
        }]
    }]
    assert mark_zero_pv_datasets(given, kind='market activity') == expected
