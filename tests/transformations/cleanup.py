# -*- coding: utf-8 -*-
from ocelot.transformations import (
    drop_zero_pv_row_datasets,
    ensure_all_datasets_have_production_volume,
)
from ocelot.transformations.cleanup import deparameterize
from ocelot.transformations.validation import (
    ensure_markets_only_have_one_reference_product,
    ensure_markets_dont_consume_their_ref_product,
)
import pytest


### Test drop_zero_pv_row_datasets function

def test_drop_zero_pv_row_datasets():
    data = [
        {
            'location': 'RoW',
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 10}
            }]
        },
        {
            'location': 'Nowhere',
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 0}
            }]
        },
        {
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
            'location': 'RoW',
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 10}
            }]
        },
        {
            'location': 'Nowhere',
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 0}
            }]
        },
    ]
    assert drop_zero_pv_row_datasets(data) == expected


### Test ensure_all_datasets_have_production_volume function

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
