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
            'name': "Fix me!, Recycled Content cut-off",
        },
    ]}]
    assert flip_non_allocatable_byproducts(given) == expected


def test_create_new_recycled_content_dataset():
    given = {
        "combined production": True,
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
    }
    expected = {
        "combined production": False,
        "exchanges": [{
            'amount': 1,
            'id': 8,
            'name': "Wowzers, Recycled Content cut-off",
            'tag': 'intermediateExchange',
            'type': 'reference product',
            'unit': 'Fun!',
        }],
        "parameters": [],
        'name': "Wowzers, Recycled Content cut-off",
        'location': 'GLO',
        'type': "transforming activity",
        'reference product': "Wowzers, Recycled Content cut-off",
        'access restricted': 1,
        'economic scenario': 2,
        'end date': 3,
        'filepath': 4,
        'id': 5,
        'start date': 6,
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
