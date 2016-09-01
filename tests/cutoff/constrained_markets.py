# -*- coding: utf-8 -*-
from ocelot.transformations.cutoff.markets import constrained_market_allocation
import pytest


def test_constrained_market_allocation(monkeypatch):
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
