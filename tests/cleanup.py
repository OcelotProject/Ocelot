# -*- coding: utf-8 -*-
from ocelot.transformations import (
    drop_zero_pv_row_datasets,
    ensure_all_datasets_have_production_volume,
    ensure_markets_only_have_one_reference_product,
    ensure_markets_dont_consume_their_ref_product,
)
from ocelot.errors import InvalidMarket, InvalidMarketExchange
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
    # TODO: Test for logging?
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

def test_ensure_markets_only_have_one_reference_product():
    given = [{
        'type': 'market activity',
        'exchanges': [
            {'type': 'reference product'},
            {'type': 'from technosphere'}
        ]
    }, {
        'type': 'transforming activity',
        'exchanges': [
            {'type': 'reference product'},
            {'type': 'reference product'},
        ]
    }]
    assert ensure_markets_only_have_one_reference_product(given)

    too_many = [{
        'type': 'market activity',
        'exchanges': [
            {'type': 'reference product'},
            {'type': 'reference product'},
        ],
        'filepath': ''
    }]
    with pytest.raises(InvalidMarket):
        ensure_markets_only_have_one_reference_product(too_many)

    too_few = [{
        'type': 'market activity',
        'exchanges': [],
        'filepath': ''
    }]
    with pytest.raises(InvalidMarket):
        ensure_markets_only_have_one_reference_product(too_few)

def test_ensure_markets_dont_consume_their_ref_product():
    good = [{
        'type': 'market activity',
        'exchanges': [
            {
                'type': 'reference product',
                'name': 'foo'
            },
            {
                'type': 'from technosphere',
                'name': 'bar'
            }
        ]
    }]
    assert ensure_markets_dont_consume_their_ref_product(good)

    bad = [{
        'type': 'market activity',
        'filepath': '',
        'exchanges': [
            {
                'type': 'reference product',
                'name': 'foo'
            },
            {
                'type': 'from technosphere',
                'name': 'foo'
            }
        ]
    }]
    with pytest.raises(InvalidMarketExchange):
        ensure_markets_dont_consume_their_ref_product(bad)
