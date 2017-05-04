# -*- coding: utf-8 -*-
from ocelot.transformations.consequential.market_linking import prune_suppliers_by_technology_level
import pytest


def test_prune_suppliers_by_technology_level():
    given = [{
        'type': 'market activity',
        'suppliers': [
            {'technology level': 'old'},
            {'technology level': 'current'},
            {'technology level': 'old'},
            {'technology level': 'current'},
        ]
    }]
    expected = [{
        'type': 'market activity',
        'suppliers': [
            {'technology level': 'current'},
            {'technology level': 'current'},
        ]
    }]
    assert prune_suppliers_by_technology_level(given) == expected

def test_prune_suppliers_by_technology_level_not_markets():
    given = [{
        'type': 'not a market activity',
        'suppliers': [
            {'technology level': 'old'},
            {'technology level': 'current'},
            {'technology level': 'old'},
            {'technology level': 'current'},
        ]
    }]
    result = prune_suppliers_by_technology_level(given)
    assert len(result[0]['suppliers']) == 4

def test_prune_suppliers_by_technology_level_no_valid_suppliers():
    error = [{
        'type': 'market activity',
        'suppliers': [{'technology level': 'not so great'}]
    }]
    with pytest.raises(AssertionError):
        prune_suppliers_by_technology_level(error)

def test_prune_suppliers_by_technology_level_no_suppliers():
    given = [{
        'type': 'market activity',
        'suppliers': []
    }]
    prune_suppliers_by_technology_level(given)
