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

    def __call__(self, x):
        return set()


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
        'suppliers': [{'code': '2',
                       'location': 'M2',
                       'name': 'market for foo',
                       'type': 'reference product'},
                      {'code': '4',
                       'location': 'G2',
                       'name': 'market group for foo',
                       'type': 'reference product'},
                      ],
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

def test_row_and_glo(monkeypatch):
    # Test that RoW and GLO are correctly populated
    # Market groups: GLO, RER (Europe), RoW, Western Europe
    # Market activities: RoW, CA, FR, NO
    # GLO Market group: RER (MG), RoW (MG)
    # RER Market group: Western Europe (MG), NO
    # Western Europe Market group: FR
    # RoW Market group: RoW (Market), CA
    monkeypatch.setattr(
        'ocelot.transformations.locations.market_groups.allocate_suppliers',
        lambda x: x
    )
    given = [{
        'type': 'market activity',
        'location': 'RoW',
        'code': '1',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'CA',
        'code': '2',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'FR',
        'code': '3',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'NO',
        'code': '4',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'GLO',
        'code': '5',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'RER',
        'code': '6',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'RoW',
        'code': '8',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'WEU',
        'code': '9',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }]
    expected = [{
        'type': 'market activity',
        'location': 'RoW',
        'code': '1',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'CA',
        'code': '2',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'FR',
        'code': '3',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'NO',
        'code': '4',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'GLO',
        'code': '5',
        'name': 'market group for foo',
        'reference product': 'foo',
        'suppliers': [{'code': '6',
                       'location': 'RER',
                       'name': 'market group for foo',
                       'type': 'reference product'},
                      {'code': '8',
                       'location': 'RoW',
                       'name': 'market group for foo',
                       'type': 'reference product'}],
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'RER',
        'code': '6',
        'name': 'market group for foo',
        'reference product': 'foo',
        'suppliers': [{'code': '4',
                       'location': 'NO',
                       'name': 'market for foo',
                       'type': 'reference product'},
                      {'code': '9',
                       'location': 'WEU',
                       'name': 'market group for foo',
                       'type': 'reference product'}],
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'RoW',
        'code': '8',
        'name': 'market group for foo',
        'reference product': 'foo',
        'suppliers': [{'code': '1',
                       'location': 'RoW',
                       'name': 'market for foo',
                       'type': 'reference product'},
                      {'code': '2',
                       'location': 'CA',
                       'name': 'market for foo',
                       'type': 'reference product'}],
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'WEU',
        'code': '9',
        'name': 'market group for foo',
        'reference product': 'foo',
        'suppliers': [{'code': '3',
                       'location': 'FR',
                       'name': 'market for foo',
                       'type': 'reference product'}],
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }]
    assert link_market_group_suppliers(given) == expected

def test_glo_includes_missing_activities(monkeypatch):
    monkeypatch.setattr(
        'ocelot.transformations.locations.market_groups.allocate_suppliers',
        lambda x: x
    )
    given = [{
        'type': 'market activity',
        'location': 'CA',
        'code': '1',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'FR',
        'code': '3',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'GLO',
        'code': '5',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'RER',
        'code': '6',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }]
    expected = [{
        'type': 'market activity',
        'location': 'CA',
        'code': '1',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'FR',
        'code': '3',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'GLO',
        'code': '5',
        'name': 'market group for foo',
        'reference product': 'foo',
        'suppliers': [{'code': '1',
                       'location': 'CA',
                       'name': 'market for foo',
                       'type': 'reference product'},
                      {'code': '6',
                       'location': 'RER',
                       'name': 'market group for foo',
                       'type': 'reference product'}],
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'RER',
        'code': '6',
        'name': 'market group for foo',
        'reference product': 'foo',
        'suppliers': [{'code': '3',
                       'location': 'FR',
                       'name': 'market for foo',
                       'type': 'reference product'}],
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }]
    assert link_market_group_suppliers(given) == expected

def test_row_includes_row(monkeypatch):
    monkeypatch.setattr(
        'ocelot.transformations.locations.market_groups.allocate_suppliers',
        lambda x: x
    )
    given = [{
        'type': 'market activity',
        'location': 'CA',
        'code': '1',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'RoW',
        'code': '3',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'RoW',
        'code': '5',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }]
    expected = [{
        'type': 'market activity',
        'location': 'CA',
        'code': '1',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'RoW',
        'code': '3',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'RoW',
        'code': '5',
        'name': 'market group for foo',
        'reference product': 'foo',
        'suppliers': [{'code': '1',
                       'location': 'CA',
                       'name': 'market for foo',
                       'type': 'reference product'},
                      {'code': '3',
                       'location': 'RoW',
                       'name': 'market for foo',
                       'type': 'reference product'}],
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }]
    assert link_market_group_suppliers(given) == expected

def test_same_location_market_group_market(monkeypatch):
    monkeypatch.setattr(
        'ocelot.transformations.locations.market_groups.allocate_suppliers',
        lambda x: x
    )
    given = [{
        'type': 'market activity',
        'location': 'CA',
        'code': '1',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'CA',
        'code': '5',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }]
    expected = [{
        'type': 'market activity',
        'location': 'CA',
        'code': '1',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'CA',
        'code': '5',
        'name': 'market group for foo',
        'reference product': 'foo',
        'suppliers': [{'code': '1',
                       'location': 'CA',
                       'name': 'market for foo',
                       'type': 'reference product'}],
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }]
    assert link_market_group_suppliers(given) == expected
