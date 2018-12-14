# -*- coding: utf-8 -*-
from ocelot.errors import OverlappingMarkets, MissingSupplier
from ocelot.transformations.locations.markets import *
from copy import deepcopy


def generate_dataset(location, name='f', rp='b', kind="market activity"):
    return {
        'name': name,
        'reference product': rp,
        'location': location,
        'code': location + name + rp,
        'technology level': 'current',
        'exchanges': [{'type': 'reference product'}],
    }

def reformat_suppliers(result):
    result_as_dict = {ds['code']: sorted([exc['code'] for exc in ds.get('suppliers', [])])
                      for ds in result}
    return {k: v for k, v in result_as_dict.items() if v}

def test_apportion_suppliers_to_consumers():
    consumers = [
        generate_dataset('UCTE without France'),
        generate_dataset('RU'),
        generate_dataset('RoW'),
    ]
    suppliers = [
        generate_dataset('FR', kind='transforming activity'),
        generate_dataset('Russia (Asia)', kind='transforming activity'),
        generate_dataset('DE', kind='transforming activity'),
        generate_dataset('MY', kind='transforming activity'),
    ]
    expected = {
        'UCTE without Francefb': ['DEfb'],
        'RUfb': ['Russia (Asia)fb'],
        'RoWfb': ['FRfb', 'MYfb']
    }
    apportion_suppliers_to_consumers(consumers, suppliers)
    assert reformat_suppliers(consumers) == expected

def test_apportion_suppliers_to_consumers_global_group():
    consumers = [
        generate_dataset('GLO'),
    ]
    suppliers = [
        generate_dataset('FR'),
        generate_dataset('Russia (Asia)'),
        generate_dataset('DE'),
        generate_dataset('MY'),
    ]
    expected = {
        'GLOfb': ['DEfb', 'FRfb', 'MYfb', 'Russia (Asia)fb'],
    }
    apportion_suppliers_to_consumers(consumers, suppliers)
    assert reformat_suppliers(consumers) == expected

def test_apportion_suppliers_to_consumers_global_supplier_excluded():
    consumers = [
        generate_dataset('NAFTA'),
    ]
    suppliers = [
        generate_dataset('GLO'),
        generate_dataset('MX'),
    ]
    expected = {
        'NAFTAfb': ['MXfb'],
    }
    apportion_suppliers_to_consumers(consumers, suppliers)
    assert reformat_suppliers(consumers) == expected

def test_apportion_suppliers_to_consumers_no_suppliers():
    consumers = [
        generate_dataset('UCTE without France'),
    ]
    apportion_suppliers_to_consumers(consumers, [])

def test_apportion_suppliers_to_consumers_nonlinked_suppliers():
    consumers = [
        generate_dataset('UCTE without France'),
    ]
    suppliers = [
        generate_dataset('FR'),
    ]
    apportion_suppliers_to_consumers(consumers, suppliers)

def test_apportion_suppliers_to_consumers_global_consumer():
    pass

def test_add_suppliers_to_markets():
    given = [{
        'type': 'skip me',
    }, {
        'code': 'cCA',
        'type': 'transforming activity',
        'reference product': 'foo',
        'technology level': 'current',
        'name': '',
        'location': 'CA',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cMX',
        'type': 'transforming activity',
        'reference product': 'foo',
        'technology level': 'current',
        'name': '',
        'location': 'MX',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cFR',
        'type': 'transforming activity',
        'reference product': 'foo',
        'technology level': 'current',
        'name': '',
        'location': 'FR',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cNAFTA',
        'type': 'market activity',
        'reference product': 'foo',
        'technology level': 'current',
        'name': '',
        'location': 'NAFTA',
    }, {
        'code': 'cRER',
        'type': 'market activity',
        'reference product': 'foo',
        'technology level': 'current',
        'name': '',
        'location': 'RER',
    }, {
        'code': 'cDE',
        'type': 'transforming activity',
        'reference product': 'bar',
        'technology level': 'current',
        'name': '',
        'location': 'DE',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cZA',
        'type': 'transforming activity',
        'reference product': 'bar',
        'technology level': 'current',
        'name': '',
        'location': 'ZA',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cRoW',
        'type': 'market activity',
        'reference product': 'bar',
        'technology level': 'current',
        'name': '',
        'location': 'RoW',
    }]
    expected = [{
        'type': 'skip me',
    }, {
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'technology level': 'current',
        'location': 'CA',
        'code': 'cCA',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'technology level': 'current',
        'location': 'MX',
        'code': 'cMX',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'technology level': 'current',
        'location': 'FR',
        'code': 'cFR',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'type': 'market activity',
        'reference product': 'foo',
        'technology level': 'current',
        'name': '',
        'location': 'NAFTA',
        'code': 'cNAFTA',
        'suppliers': [
            {
                'code': 'cCA',
                'location': 'CA',
                'type': 'reference product',
                'technology level': 'current',
                'name': '',
            },
            {
                'code': 'cMX',
                'location': 'MX',
                'technology level': 'current',
                'type': 'reference product',
                'name': ''
            }
        ]
    }, {
        'type': 'market activity',
        'reference product': 'foo',
        'technology level': 'current',
        'name': '',
        'location': 'RER',
        'code': 'cRER',
        'suppliers': [{
            'code': 'cFR',
            'type': 'reference product',
            'technology level': 'current',
            'location': 'FR',
            'name': ''
        }]
    }, {
        'type': 'transforming activity',
        'reference product': 'bar',
        'technology level': 'current',
        'name': '',
        'location': 'DE',
        'code': 'cDE',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'type': 'transforming activity',
        'reference product': 'bar',
        'technology level': 'current',
        'name': '',
        'location': 'ZA',
        'code': 'cZA',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'type': 'market activity',
        'reference product': 'bar',
        'technology level': 'current',
        'name': '',
        'location': 'RoW',
        'code': 'cRoW',
        'suppliers': [{
            'code': 'cDE',
            'location': 'DE',
            'technology level': 'current',
            'type': 'reference product',
            'name': '',
        }, {
            'code': 'cZA',
            'location': 'ZA',
            'type': 'reference product',
            'technology level': 'current',
            'name': '',
        }]
    }]
    assert add_suppliers_to_markets(given) == expected

def test_add_suppliers_to_markets():
    given = [{
        'type': 'skip me',
        'code': 'foo',
    }, {
        'code': 'cCA',
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'location': 'CA',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cMX',
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'location': 'MX',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cFR',
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'location': 'FR',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cNAFTA',
        'type': 'market activity',
        'reference product': 'foo',
        'name': '',
        'location': 'NAFTA',
    }, {
        'code': 'cRER',
        'type': 'market activity',
        'reference product': 'foo',
        'name': '',
        'location': 'RER',
    }, {
        'code': 'cDE',
        'type': 'transforming activity',
        'reference product': 'bar',
        'name': '',
        'location': 'DE',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cZA',
        'type': 'transforming activity',
        'reference product': 'bar',
        'name': '',
        'location': 'ZA',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cRoW',
        'type': 'market activity',
        'reference product': 'bar',
        'name': '',
        'location': 'RoW',
    }]
    expected = {
        'cRoW': ['cDE', 'cZA'],
        'cRER': ['cFR'],
        'cNAFTA': ['cCA', 'cMX'],
    }
    assert reformat_suppliers(add_suppliers_to_markets(given)) == expected

def test_add_suppliers_to_markets_no_consumers():
    given = [{
        'code': 'cCA',
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'location': 'CA',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cMX',
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'location': 'MX',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cFR',
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'location': 'FR',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cNAFTA',
        'type': 'market activity',
        'reference product': 'bar',
        'name': '',
        'location': 'NAFTA',
    }, {
        'code': 'cRER',
        'type': 'market activity',
        'reference product': 'bar',
        'name': '',
        'location': 'RER',
    }]
    expected = deepcopy(given)
    expected[3]['suppliers'] = []
    expected[4]['suppliers'] = []
    assert add_suppliers_to_markets(given) == expected

def test_allocate_all_market_suppliers():
    given = [{
        'location': 'dining room',
        'name': 'dinner',
        'type': 'market activity',
        'exchanges': [{
            'amount': 24,
            'name': 'salad',
            'type': 'reference product',
        }],
        'suppliers': [{
            'code': 'up',
            'location': 'upstairs',
            'name': '',
            'production volume': {'amount': 2},
            'unit': '',
        }, {
            'code': 'do',
            'location': 'downstairs',
            'name': '',
            'production volume': {'amount': 10},
            'unit': '',
        }]
    }]
    expected = [{
        'amount': 24,
        'name': 'salad',
        'type': 'reference product',
    }, {
        'amount': 2 / 12 * 24,
        'code': 'up',
        'name': '',
        'tag': 'intermediateExchange',
        'type': 'from technosphere',
        'unit': '',
    }, {
        'amount': 10 / 12 * 24,
        'code': 'do',
        'name': '',
        'tag': 'intermediateExchange',
        'type': 'from technosphere',
        'unit': '',
    }]
    assert allocate_all_market_suppliers(deepcopy(given))[0]['exchanges'] == expected

def test_allocate_all_market_suppliers_single_supplier():
    given = [{
        'location': 'dining room',
        'name': 'dinner',
        'type': 'market activity',
        'exchanges': [{
            'amount': 24,
            'name': 'salad',
            'type': 'reference product',
        }],
        'suppliers': [{
            'code': 'up',
            'location': 'upstairs',
            'name': '',
            'production volume': {'amount': 20},
            'unit': '',
        }]
    }]
    expected = [{
        'amount': 24,
        'name': 'salad',
        'type': 'reference product',
    }, {
        'amount': 24,
        'code': 'up',
        'name': '',
        'tag': 'intermediateExchange',
        'type': 'from technosphere',
        'unit': '',
    }]
    assert allocate_all_market_suppliers(deepcopy(given))[0]['exchanges'] == expected

def test_update_market_production_volumes():
    given = [{
        'name': '',
        'type': 'foo',
        'location': '',
        'exchanges': [{
            'name': '',
            'type': 'reference product',
            'production volume': {}
        }],
        'suppliers': [
            {'production volume': {'amount': 10}},
            {'production volume': {'amount': 20}},
        ]
    }]
    ds = update_market_production_volumes(given, 'foo')[0]
    assert ds['exchanges'][0]['production volume']['amount'] == 30

def test_update_market_production_volumes_activity_link():
    given = [{
        'name': '',
        'type': 'foo',
        'location': '',
        'exchanges': [{
            'name': '',
            'type': 'reference product',
            'production volume': {'subtracted activity link volume': 15}
        }],
        'suppliers': [
            {'production volume': {
                'amount': 10,
                'subtracted activity link volume': 8
            }},
            {'production volume': {'amount': 20}},
        ]
    }]
    ds = update_market_production_volumes(given, 'foo')[0]
    assert ds['exchanges'][0]['production volume']['amount'] == 7

def test_update_market_production_volumes_negative_sum():
    given = [{
        'name': '',
        'type': 'foo',
        'location': '',
        'exchanges': [{
            'name': '',
            'type': 'reference product',
            'production volume': {'subtracted activity link volume': 40}
        }],
        'suppliers': [
            {'production volume': {'amount': 10}},
            {'production volume': {'amount': 20}},
        ]
    }]
    ds = update_market_production_volumes(given, 'foo')[0]
    assert ds['exchanges'][0]['production volume']['amount'] == 0

def test_delete_suppliers_list():
    given = [{'suppliers': 1}]
    assert delete_suppliers_list(given) == [{}]

def test_assign_fake_pv_to_confidential_datasets():
    given = [{
        'name': "latex production",
        'type': 'transforming activity',
        'location': 'GLO',
        'exchanges': [{
            'type': 'reference product',
            'name': '',
            'production volume': {}
        }]
    }]
    expected = [{
        'name': "latex production",
        'type': 'transforming activity',
        'location': 'GLO',
        'exchanges': [{
            'type': 'reference product',
            'name': '',
            'production volume': {'amount': 1}
        }]
    }]
    assert assign_fake_pv_to_confidential_datasets(given) == expected
    del given[0]['exchanges'][0]['production volume']['amount']
    assert given != expected
    given[0]['type'] = 'market activity'
    assert assign_fake_pv_to_confidential_datasets(given) != expected
    given[0]['type'] = 'transforming activity'
    assert assign_fake_pv_to_confidential_datasets(given) == expected

def test_delete_allowed_zero_pv_market_datsets():
    given = [{
        'type': 'market activity',
        'name': 'not market for refinery gas',
        'location': 'GLO',
        'reference product': '',
    }, {
        'type': 'market activity',
        'name': 'market for refinery gas',
        'location': 'GLO',
        'reference product': '',
    }]
    expected = [{
        'type': 'market activity',
        'name': 'not market for refinery gas',
        'location': 'GLO',
        'reference product': '',
    }]
    assert delete_allowed_zero_pv_market_datsets(given) == expected

def test_allocate_suppliers_no_production_volume_single_supplier():
    given = {
        'name': '',
        'location': '',
        'exchanges': [{
            'type': 'reference product',
            'name': '',
            'amount': 1,
        }],
        'suppliers': [{
            'production volume': {'amount': 0},
            'name': 'a',
            'unit': 'b',
            'code': 'foo',
            'location': '',
        }]
    }
    expected = {
        'name': '',
        'location': '',
        'exchanges': [{
            'type': 'reference product',
            'name': '',
            'amount': 1,
        }, {
            'amount': 1,
            'name': 'a',
            'unit': 'b',
            'code': 'foo',
            'type': 'from technosphere',
            'tag': 'intermediateExchange',
        }],
        'suppliers': [{
            'production volume': {'amount': 4321},
            'name': 'a',
            'unit': 'b',
            'code': 'foo',
            'location': '',
        }]
    }
    assert allocate_suppliers(given) == expected

def test_allocate_suppliers_no_production_volume():
    given = {
        'name': '',
        'location': '',
        'exchanges': [{
            'type': 'reference product',
            'name': '',
            'amount': 1,
        }],
        'suppliers': [{
            'production volume': {'amount': 0}
        }, {
            'production volume': {'amount': 0}
        }]
    }
    assert allocate_suppliers(given) is None

def test_allocate_suppliers_skip_zero_amount():
    given = {
        'exchanges': [{
            'type': 'reference product',
            'name': '',
            'amount': 1,
        }],
        'suppliers': [{
            'name': 'skip me',
            'amount': 1,
            'production volume': {'amount': 0},
        }, {
            'name': 'keep me',
            'unit': '',
            'location': '',
            'code': '',
            'amount': 1,
            'production volume': {'amount': 1},

        }]
    }
    expected = {
        'exchanges': [{
            'type': 'reference product',
            'name': '',
            'amount': 1,
        }, {
            'amount': 1,
            'code': '',
            'name': 'keep me',
            'tag': 'intermediateExchange',
            'type': 'from technosphere',
            'unit': '',
        }],
        'suppliers': [{
            'name': 'skip me',
            'amount': 1,
            'production volume': {'amount': 0},
        }, {
            'name': 'keep me',
            'unit': '',
            'location': '',
            'code': '',
            'amount': 1,
            'production volume': {'amount': 1},

        }]
    }
    assert allocate_suppliers(given) == expected

def test_add_recycled_content_suppliers_to_markets():
    given = [{
        'code': 'cCA',
        'type': 'transforming activity',
        'reference product': 'foo, Recycled Content cut-off',
        'name': '',
        'location': 'CA',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cMX',
        'type': 'transforming activity',
        'reference product': 'foo, Recycled Content cut-off',
        'name': '',
        'location': 'MX',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cFR',
        'type': 'transforming activity',
        'reference product': 'foo, Recycled Content cut-off',
        'name': '',
        'location': 'FR',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cNAFTA',
        'type': 'market activity',
        'reference product': 'foo',
        'name': '',
        'location': 'NAFTA',
    }, {
        'code': 'cRER',
        'type': 'market activity',
        'reference product': 'foo',
        'name': '',
        'location': 'RER',
    }, {
        'code': 'cDE',
        'type': 'transforming activity',
        'reference product': 'bar',
        'name': '',
        'location': 'DE',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cZA',
        'type': 'transforming activity',
        'reference product': 'bar',
        'name': '',
        'location': 'ZA',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cRoW',
        'type': 'market activity',
        'reference product': 'bar',
        'name': '',
        'location': 'RoW',
    }]
    expected = [{
        'type': 'transforming activity',
        'reference product': 'foo, Recycled Content cut-off',
        'name': '',
        'location': 'CA',
        'code': 'cCA',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'type': 'transforming activity',
        'reference product': 'foo, Recycled Content cut-off',
        'name': '',
        'location': 'MX',
        'code': 'cMX',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'type': 'transforming activity',
        'reference product': 'foo, Recycled Content cut-off',
        'name': '',
        'location': 'FR',
        'code': 'cFR',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'type': 'market activity',
        'reference product': 'foo',
        'name': '',
        'location': 'NAFTA',
        'code': 'cNAFTA',
        'suppliers': [
            {
                'code': 'cCA',
                'location': 'CA',
                'type': 'reference product',
                'activity': '',
            },
            {
                'code': 'cMX',
                'location': 'MX',
                'type': 'reference product',
                'activity': ''
            }
        ]
    }, {
        'type': 'market activity',
        'reference product': 'foo',
        'name': '',
        'location': 'RER',
        'code': 'cRER',
        'suppliers': [{
            'code': 'cFR',
            'type': 'reference product',
            'location': 'FR',
            'activity': ''
        }]
    }, {
        'type': 'transforming activity',
        'reference product': 'bar',
        'name': '',
        'location': 'DE',
        'code': 'cDE',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'type': 'transforming activity',
        'reference product': 'bar',
        'name': '',
        'location': 'ZA',
        'code': 'cZA',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'type': 'market activity',
        'reference product': 'bar',
        'name': '',
        'location': 'RoW',
        'code': 'cRoW',
    }]
    assert add_recycled_content_suppliers_to_markets(given) == expected
