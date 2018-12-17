# -*- coding: utf-8 -*-
from ocelot.transformations.locations.market_groups import *
from ocelot.errors import MarketGroupError
import pytest


class FakeTopology:
    def tree(self, data):
        return {
            'G1': {
                'G2': {'M1': {}},
                'M2': {}
            }
        }

    def ordered_dependencies(self, datasets):
        locations = {x['location'] for x in datasets}
        return [x for x in ['G1', 'G2', 'M1', 'M2'] if x in locations]

    def contained(self, location, exclude_self=False, subtract=None,
            resolved_row=None):
        if location == 'G1':
            return {'G2', 'M1', 'M2'}
        elif location == 'G2':
            return {'M1'}
        else:
            return set()

    def contains(self, parent, child, subtract=None, resolved_row=None):
        if parent == 'G1' and child in {'M1', 'M2', 'G2'}:
            return True
        elif parent == 'G2' and child == 'M1':
            return True
        else:
            return False

    def __call__(self, x):
        return set()


def reformat_suppliers(result):
    result_as_dict = {ds['code']: sorted([exc['code'] for exc in ds.get('suppliers', [])])
                      for ds in result}
    return {k: v for k, v in result_as_dict.items() if v}

def test_inconsistent_names():
    data = [{
        'type': 'market group',
        'name': 'market group for bar',
        'reference product': 'foo',
    }, {
        'type': 'market group',
        'name': 'market group for foo',
        'reference product': 'foo',
    }]
    with pytest.raises(MarketGroupError):
        link_market_group_suppliers(data)

def test_real_locations_including_glo_but_excluding_row():
    # Markets: RoW, CA, FR, NO
    # Market groups: GLO, RER, WEU (Western Europe)
    expected = {
        "GLO": ['CA', 'RER', 'RoW'],
        "RER": ['NO', 'WEU'],
        "WEU": ['FR'],

    }
    given = [{
        'type': 'market activity',
        'location': 'RoW',
        'code': 'RoW',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'CA',
        'code': 'CA',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'FR',
        'code': 'FR',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'NO',
        'code': 'NO',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'GLO',
        'code': 'GLO',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'RER',
        'code': 'RER',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'WEU',
        'code': 'WEU',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }]
    assert reformat_suppliers(link_market_group_suppliers(given)) == expected

def test_real_locations_including_glo_and_row():
    # Markets: RoW, CA, FR, NO
    # Market groups: GLO, RER, WEU (Western Europe)
    expected = {
        "GLO": ['CA', 'RER', 'RoW'],
        "RER": ['NO', 'WEU'],
        "WEU": ['FR'],

    }
    given = [{
        'type': 'market activity',
        'location': 'RoW',
        'code': 'RoW',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'CA',
        'code': 'CA',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'FR',
        'code': 'FR',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'NO',
        'code': 'NO',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'GLO',
        'code': 'GLO',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'RER',
        'code': 'RER',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'WEU',
        'code': 'WEU',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }]
    assert reformat_suppliers(link_market_group_suppliers(given)) == expected

def test_glo_includes_missing_activities():
    given = [{
        'type': 'market activity',
        'location': 'CA',
        'code': 'CA',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'FR',
        'code': 'FR',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'GLO',
        'code': 'GLO',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'RER',
        'code': 'RER',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }]
    expected = {
        "GLO": ['CA', 'RER'],
        "RER": ['FR'],

    }
    assert reformat_suppliers(link_market_group_suppliers(given)) == expected

def test_same_location_market_group_market():
    given = [{
        'type': 'market activity',
        'location': 'CA',
        'code': '2',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'CA',
        'code': '1',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }]
    expected = {
        "1": ['2'],
    }
    assert reformat_suppliers(link_market_group_suppliers(given)) == expected

def test_row_only_supply_no_market_group():
    given = [{
        'type': 'market activity',
        'location': 'RoW',
        'code': 'RoW',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'RER',
        'code': 'RER',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'GLO',
        'code': 'GLO',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }]
    expected = {
        "GLO": ['RER', 'RoW'],
    }
    assert reformat_suppliers(link_market_group_suppliers(given)) == expected

def test_row_market_groups():
    data = [{
        'type': 'market group',
        'location': 'RoW',
    }]
    with pytest.raises(MarketGroupError):
        check_no_row_market_groups(data)
