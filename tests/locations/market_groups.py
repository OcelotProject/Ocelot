# -*- coding: utf-8 -*-
from ocelot.transformations.locations.market_groups import *
import pytest


class FakeTopology:
    def tree(self, data):
        return {
            'G1': {
                'G2': {'M1': {}},
                'M2': {}
            }
        }


@pytest.fixture(scope="function")
def group_fixture(monkeypatch):
    monkeypatch.setattr(
        'ocelot.transformations.locations.market_groups.topology',
        FakeTopology()
    )
    monkeypatch.setattr(
        'ocelot.transformations.locations.market_groups.allocate_suppliers',
        lambda x: x
    )
    data = [{
        'type': 'market activity',
        'location': 'M1',
        'code': '1',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{
            'type': 'reference product',
            'name': 'foo',
        }]
    }, {
        'type': 'market activity',
        'location': 'M2',
        'code': '2',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{
            'type': 'reference product',
            'name': 'foo',
        }]
    }, {
        'type': 'market group',
        'location': 'G1',
        'code': '3',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{
            'type': 'reference product',
            'name': 'foo',
        }]
    }, {
        'type': 'market group',
        'location': 'G2',
        'code': '4',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{
            'type': 'reference product',
            'name': 'foo',
        }]
    }]
    return data


def test_link_market_group_suppliers(group_fixture):
    expected = [{
        'type': 'market activity',
        'location': 'M1',
        'code': '1',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{
            'type': 'reference product',
            'name': 'foo',
        }]
    }, {
        'type': 'market activity',
        'location': 'M2',
        'code': '2',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{
            'type': 'reference product',
            'name': 'foo',
        }]
    }, {
        'type': 'market group',
        'location': 'G1',
        'code': '3',
        'name': 'market group for foo',
        'reference product': 'foo',
        'suppliers': [{'code': '4',
                       'location': 'G2',
                       'name': 'market group for foo',
                       'type': 'reference product'},
                      {'code': '2',
                       'location': 'M2',
                       'name': 'market for foo',
                       'type': 'reference product'}],
        'exchanges': [{
            'type': 'reference product',
            'name': 'foo',
        }]
    }, {
        'type': 'market group',
        'location': 'G2',
        'code': '4',
        'name': 'market group for foo',
        'reference product': 'foo',
        'suppliers': [{'code': '1',
                       'location': 'M1',
                       'name': 'market for foo',
                       'type': 'reference product'}],
        'exchanges': [{
            'type': 'reference product',
            'name': 'foo',
        }]
    }]
    assert link_market_group_suppliers(group_fixture) == expected