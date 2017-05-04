# -*- coding: utf-8 -*-
from ocelot.errors import MissingAlternativeProducer
from ocelot.transformations.consequential.byproducts import ensure_byproducts_have_alternative_production
import pytest


def test_ensure_byproducts_have_alternative_production():
    given = [{
        'exchanges': [{
            'name': 'foo',
            'type': 'reference product',
        }, {
            'name': 'foo',
            'type': 'byproduct'
        }]
    }]
    assert ensure_byproducts_have_alternative_production(given)

    given = [{
        'exchanges': [{
            'name': 'foo',
            'type': 'reference product',
        }, {
            'name': 'bar',
            'type': 'byproduct'
        }]
    }]
    with pytest.raises(MissingAlternativeProducer):
        ensure_byproducts_have_alternative_production(given)
