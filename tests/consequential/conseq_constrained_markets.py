# -*- coding: utf-8 -*-
from ocelot.transformations.consequential.constrained_markets import (
    handle_constrained_markets,
    flip_exchange,
)
from copy import deepcopy
import pytest


def test_flip_exchange():
    given = {
        'amount': 1,
        'formula': 'a'
    }
    expected = {
        'amount': -1,
        'formula': '-1 * (a)'
    }
    assert flip_exchange(given) == expected
    given = {'amount': 1}
    expected = {'amount': -1}
    assert flip_exchange(given) == expected

@pytest.fixture
def fluosilicic():
    return [{
        'name': 'market for fluosilicic acid',
        'type': 'market activity',
        'id': 'the market',
        'exchanges': [{
            'amount': 1,
            'name': 'fluosilicic acid',
            'type': 'reference product',
        }, {
            'amount': -1,
            'conditional exchange': True,
            'name': 'fluosilicic acid',
            'type': 'byproduct',
            'activity link': 'the producer'
        }]
    }, {
        'name': 'cryolite production',
        'type': 'transforming activity',
        'id': 'the producer',
        'exchanges': [{
            'amount': 1,
            'name': 'cryolite',
            'type': 'reference product',
        }, {
            'amount': 0.7,
            'name': 'fluosilicic acid',
            'type': 'from technosphere',
        }, {
            'name': 'electricity',
            'amount': 0.3,
            'type': 'from technosphere'
        }]
    }]

def test_handle_constrained_markets(fluosilicic):
    expected = [{
        'name': 'market for fluosilicic acid',
        'type': 'market activity',
        'id': 'the market',
        'exchanges': [{
            'amount': 1,
            'name': 'fluosilicic acid',
            'type': 'reference product',
        }, {
            'amount': 1,
            'conditional exchange': True,
            'name': 'fluosilicic acid',
            'type': 'from technosphere',
            'activity link': 'the producer'
        }]
    }, {
        'name': 'cryolite production',
        'type': 'transforming activity',
        'id': 'the producer',
        'exchanges': [{
            'amount': -1,
            'name': 'cryolite',
            'type': 'from technosphere',
        }, {
            'amount': -0.7,
            'name': 'fluosilicic acid',
            'type': 'reference product',
            'byproduct classification': 'allocatable product',
        }, {
            'name': 'electricity',
            'amount': 0.3,
            'type': 'from technosphere'
        }]
    }]
    assert handle_constrained_markets(fluosilicic) == expected

def test_handle_constrained_markets_no_target_exchanges(fluosilicic):
    assert len(fluosilicic[1]['exchanges']) == 3
    del fluosilicic[1]['exchanges'][1]
    with pytest.raises(AssertionError):
        handle_constrained_markets(fluosilicic)

def test_handle_constrained_markets_wrong_target_exchange_type(fluosilicic):
    assert fluosilicic[1]['exchanges'][1]['type'] == 'from technosphere'
    fluosilicic[1]['exchanges'][1]['type'] = 'byproduct'
    with pytest.raises(AssertionError):
        handle_constrained_markets(fluosilicic)
