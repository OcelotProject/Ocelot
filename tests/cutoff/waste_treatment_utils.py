# -*- coding: utf-8 -*-
from ocelot.transformations.cutoff.wastes import *
import pytest


def test_flip_non_allocatable_byproducts():
    given = {
        'something else': 'woo!',
        'name': 'a name',
        'exchanges': [
        {
            'type': 'reference product',
            'amount': 1,
        },
        {
            'type': 'byproduct',
            'name': 2,
            'byproduct classification': 'allocatable product',
            'amount': 2,
        },
        {
            'type': 'byproduct',
            'byproduct classification': 'waste',
            'name': 3,
            'amount': 3,
        },
        {
            'type': 'byproduct',
            'byproduct classification': 'recyclable',
            'amount': 4,
            'formula': 'foo',
            'name': "Fix me!",
        },
    ]}
    expected = [{
        'something else': 'woo!',
        'name': 'a name',
        'exchanges': [
        {
            'type': 'reference product',
            'amount': 1,
        },
        {
            'type': 'byproduct',
            'byproduct classification': 'allocatable product',
            'name': 2,
            'amount': 2,
        },
        {
            'type': 'from technosphere',
            'name': 3,
            'amount': -3,
        },
        {
            'type': 'from technosphere',
            'amount': -4,
            'formula': '-1 * (foo)',
            'name': "Fix me!",
        },
    ]}]
    assert flip_non_allocatable_byproducts(given) == expected


def test_create_new_recycled_content_dataset():
    given = {
        "exchanges": [{}, {
            'id': 8,
            'name': "Wowzers",
            'unit': 'Fun!',
        }],
        'access restricted': 1,
        'economic scenario': 2,
        'end date': 3,
        'filepath': 4,
        'id': 5,
        'start date': 6,
        'technology level': 7,
        'dataset author': 'blue',
        'data entry': 'green',
    }
    expected = {
        "exchanges": [{
            'amount': 1,
            'id': 8,
            'name': "Wowzers",
            'tag': 'intermediateExchange',
            'type': 'reference product',
            'production volume': {'amount': 4},
            'unit': 'Fun!',
        }],
        "parameters": [],
        'name': "Wowzers",
        'location': 'GLO',
        'type': "transforming activity",
        'reference product': "Wowzers",
        'access restricted': 1,
        'economic scenario': 2,
        'end date': 3,
        'filepath': 4,
        'id': 5,
        'start date': 6,
        'dataset author': 'blue',
        'data entry': 'green',
        'technology level': 7,
    }
    assert create_new_recycled_content_dataset(given, given['exchanges'][1]) == expected

def test_create_recycled_content_datasets(monkeypatch):
    monkeypatch.setattr(
        'ocelot.transformations.cutoff.wastes.create_new_recycled_content_dataset',
        lambda x, y: {'name': y['name']}
    )
    given = [{
        'name': 'foo',
        'exchanges': [{
            'type': 'nope'
        }, {
            'type': 'byproduct',
            'byproduct classification': 'recyclable',
            'name': 'henry',
        }, {
            'type': 'byproduct',
            'byproduct classification': 'recyclable',
            'name': 'henrietta',
        }]
    }]
    expected = {
        'name': 'foo',
        'exchanges': [{
            'type': 'nope'
        }, {
            'type': 'byproduct',
            'byproduct classification': 'recyclable',
            'name': 'henry',
        }, {
            'type': 'byproduct',
            'byproduct classification': 'recyclable',
            'name': 'henrietta',
        }]
    }
    result = create_recycled_content_datasets(given)
    assert result[0] == expected
    assert len(result) == 3
    assert {'name': 'henry'} in result
    assert {'name': 'henrietta'} in result

def test_rename_recycled_content_products_after_linking():
    given = [{'exchanges': [{
        'name': 'foo',
    }, {
        'name': 'bar, Recycled Content cut-off'
    }]}]
    expected = [{'exchanges': [{
        'name': 'foo',
    }, {
        'name': 'bar'
    }]}]
    assert rename_recycled_content_products_after_linking(given) == expected

def test_rename_recyclable_content_exchanges():
    given = [{'exchanges': [{
        'type': 'product',
        'byproduct classification': 'recyclable',
        'name': '1',
    }, {
        'type': 'byproduct',
        'byproduct classification': 'recyclable',
        'name': '2',
    }, {
        'type': 'byproduct',
        'byproduct classification': 'waste',
        'name': '3',
    }]}]
    expected = [{'exchanges': [{
        'type': 'product',
        'byproduct classification': 'recyclable',
        'name': '1',
    }, {
        'type': 'byproduct',
        'byproduct classification': 'recyclable',
        'name': '2, Recycled Content cut-off',
    }, {
        'type': 'byproduct',
        'byproduct classification': 'waste',
        'name': '3',
    }]}]
    assert rename_recyclable_content_exchanges(given) == expected
