# -*- coding: utf-8 -*-
from ocelot.errors import (
    IdenticalDatasets,
    InvalidExchange,
    InvalidMarket,
    InvalidMarketExchange,
    InvalidMultioutputDataset,
    MissingMandatoryProperty,
)
from ocelot.transformations.validation import (
    check_single_output_activity,
    ensure_ids_are_unique,
    ensure_mandatory_properties,
    ensure_markets_dont_consume_their_ref_product,
    ensure_markets_only_have_one_reference_product,
    ensure_production_exchanges_have_production_volume,
)
import pytest


def test_ensure_ids_are_unique():
    correct = [
        {'id': 1},
        {'id': 2}
    ]
    assert ensure_ids_are_unique(correct)
    incorrect = [
        {'id': 1},
        {'id': 1}
    ]
    with pytest.raises(IdenticalDatasets):
        ensure_ids_are_unique(incorrect)

def test_check_single_output():
    ds = {'exchanges': [{
        'type': 'reference product'
    }]}
    assert check_single_output_activity(ds)
    assert check_single_output_activity(ds) is ds

def test_no_reference_product():
    ds = {'exchanges': [{
        'type': 'to environment'
    }]}
    with pytest.raises(InvalidMultioutputDataset):
        check_single_output_activity(ds)

def test_correct_byproduct():
    ds = {'exchanges': [{
        'type': 'reference product',
    }, {
        'type': 'byproduct',
        'byproduct classification': 'waste'
    }]}
    assert check_single_output_activity(ds)

def test_wrong_byproduct():
    ds = {'exchanges': [{
        'type': 'reference product',
    }, {
        'type': 'byproduct',
        'byproduct classification': 'allocatable product'
    }]}
    with pytest.raises(InvalidMultioutputDataset):
        check_single_output_activity(ds)

def test_multiple_reference_products():
    ds = {'exchanges': [{
        'type': 'reference product',
    }, {
        'type': 'reference product',
    }]}
    with pytest.raises(InvalidMultioutputDataset):
        check_single_output_activity(ds)

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

def test_ensure_mandatory_properties():
    given = [{'exchanges': [{
            'name': 'something',
            'type': 'from technosphere'
        }]
    }]
    assert ensure_mandatory_properties(given)

    # missing = [{
    #     'filepath': '',
    #     'exchanges': [{
    #         'name': 'something',
    #         'type': 'from technosphere',
    #         'properties': [
    #             {'amount': 1, 'name': "dry mass"},
    #             {'amount': 1, 'name': "water in wet mass"},
    #             {'amount': 1, 'name': "wet mass"},
    #             {'amount': 1, 'name': "water content"},
    #             {'amount': 1, 'name': "carbon content fossil"},
    #         ]
    #     }]
    # }]
    # with pytest.raises(MissingMandatoryProperty):
    #     ensure_mandatory_properties(missing)

    missing = [{
        'filepath': '',
        'exchanges': [{
            'name': 'something',
            'type': 'from technosphere',
            'properties': [
                {'amount': 1, 'name': "dry mass"},
                {'amount': 1, 'name': "water in wet mass"},
                {'amount': 1, 'name': "wet mass"},
                {'name': "water content"},
                {'amount': 1, 'name': "carbon content fossil"},
                {'amount': 1, 'name': "carbon content non-fossil"},
            ]
        }]
    }]
    with pytest.raises(ValueError):
        ensure_mandatory_properties(missing)

def test_ensure_production_exchanges_have_production_volume():
    data = [{'exchanges':
        [{
            'type': 'reference product',
            'production volume': None
        }]
    }]
    assert ensure_production_exchanges_have_production_volume(data)

    data = [{
        'filepath': '',
        'exchanges': [{'type': 'reference product'}]
    }]
    with pytest.raises(InvalidExchange):
        ensure_production_exchanges_have_production_volume(data)
