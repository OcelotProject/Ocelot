# -*- coding: utf-8 -*-
from ocelot.transformations.cutoff.markets import constrained_market_allocation
import pytest


def test_constrained_market_allocation(monkeypatch):
    """This test literally does nothing useful, and is included only to make sure that this function doesn't produce an error when called with valid data"""
    def visit_exchange(exc):
        exc['touched'] = True

    monkeypatch.setattr(
        'ocelot.transformations.cutoff.markets.nonreference_product',
        visit_exchange
    )
    given = {
        'name': 'a name',
        'exchanges': [
            {'type': 'foo'},
            {'type': 'byproduct'},
            {
                'conditional exchange': True,
                'name': 'another name',
                'type': 'byproduct',
            },
            {'type': 'byproduct', 'conditional exchange': False},
            {'type': 'other', 'conditional exchange': True},
        ]
    }
    expected = {
        'name': 'a name',
        'exchanges': [
            {'type': 'foo'},
            {'type': 'byproduct'},
            {
                'conditional exchange': True,
                'name': 'another name',
                'touched': True,
                'type': 'byproduct',
            },
            {'type': 'byproduct', 'conditional exchange': False},
            {'type': 'other', 'conditional exchange': True},
        ]
    }
    assert constrained_market_allocation(given) == expected
