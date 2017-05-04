# -*- coding: utf-8 -*-
from ocelot.errors import OverlappingMarkets, MissingSupplier
from ocelot.transformations.locations.markets import *
from copy import deepcopy


def generate_dataset(location, name='foo', rp='bar'):
    return {
        'name': name,
        'reference product': rp,
        'location': location,
        'code': location + name + rp,
        'technology level': 'current',
    }

def test_apportion_suppliers_to_consumers():
    consumers = [
        generate_dataset('UCTE without France'),
        generate_dataset('RU'),
        generate_dataset('RoW'),
    ]
    suppliers = [
        generate_dataset('FR'),
        generate_dataset('Russia (Asia)'),
        generate_dataset('DE'),
        generate_dataset('MY'),
    ]
    for s in suppliers:
        s.update({'exchanges': [{'type': 'reference product'}]})
    expected = [{
        'code': 'UCTE without Francefoobar',
        'reference product': 'bar',
        'name': 'foo',
        'technology level': 'current',
        'location': 'UCTE without France',
        'suppliers': [{
            'type': 'reference product',
            'location': 'DE',
            'technology level': 'current',
            'code': 'DEfoobar',
            'name': 'foo',
        }]
    }, {
        'code': 'RUfoobar',
        'reference product': 'bar',
        'name': 'foo',
        'technology level': 'current',
        'location': 'RU',
        'suppliers': [{
            'type': 'reference product',
            'location': 'Russia (Asia)',
            'code': 'Russia (Asia)foobar',
            'technology level': 'current',
            'name': 'foo'
        }]
    }, {
        'code': 'RoWfoobar',
        'reference product': 'bar',
        'name': 'foo',
        'technology level': 'current',
        'location': 'RoW',
        'suppliers': [
            {
                'type': 'reference product',
                'location': 'FR',
                'technology level': 'current',
                'code': 'FRfoobar',
                'name': 'foo',
            }, {
                'type': 'reference product',
                'location': 'MY',
                'technology level': 'current',
                'code': 'MYfoobar',
                'name': 'foo',
            }
        ]
    }]
    apportion_suppliers_to_consumers(consumers, suppliers)
    assert consumers == expected

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
    for s in suppliers:
        s.update({'exchanges': [{'type': 'reference product'}]})
    expected = [{
        'code': 'GLOfoobar',
        'reference product': 'bar',
        'name': 'foo',
        'location': 'GLO',
        'technology level': 'current',
        'suppliers': [{
            'type': 'reference product',
            'location': 'DE',
            'code': 'DEfoobar',
            'technology level': 'current',
            'name': 'foo',
        }, {
            'type': 'reference product',
            'location': 'FR',
            'code': 'FRfoobar',
            'technology level': 'current',
            'name': 'foo',
        }, {
            'type': 'reference product',
            'location': 'MY',
            'code': 'MYfoobar',
            'technology level': 'current',
            'name': 'foo',
        }, {
            'type': 'reference product',
            'location': 'Russia (Asia)',
            'code': 'Russia (Asia)foobar',
            'technology level': 'current',
            'name': 'foo'
        }]
    }]
    apportion_suppliers_to_consumers(consumers, suppliers)
    consumers[0]['suppliers'].sort(key = lambda x: x['location'])
    expected[0]['suppliers'].sort(key = lambda x: x['location'])
    assert consumers == expected

def test_apportion_suppliers_to_consumers_global_supplier_excluded():
    suppliers = [{
        'code': 'a',
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': 'first',
        'location': 'GLO',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'b',
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': 'second',
        'location': 'MX',
        'exchanges': [{'type': 'reference product'}],
    }]
    consumers = [{
        'code': 'c',
        'type': 'market activity',
        'reference product': 'foo',
        'name': '',
        'location': 'NAFTA',
    }]
    expected = [{
        'code': 'c',
        'reference product': 'foo',
        'type': 'market activity',
        'name': '',
        'location': 'NAFTA',
        'suppliers': [{
            'type': 'reference product',
            'location': 'MX',
            'code': 'b',
            'name': 'second',
        }]
    }]
    apportion_suppliers_to_consumers(consumers, suppliers)
    consumers[0]['suppliers'].sort(key = lambda x: x['location'])
    expected[0]['suppliers'].sort(key = lambda x: x['location'])
    assert consumers == expected

def test_apportion_suppliers_to_consumers_global_supplier_included():
    suppliers = [{
        'code': 'a',
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': 'first',
        'location': 'GLO',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'b',
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': 'second',
        'location': 'MX',
        'exchanges': [{'type': 'reference product'}],
    }]
    consumers = [{
        'code': 'c',
        'type': 'market activity',
        'reference product': 'foo',
        'name': '',
        'location': 'RoW',
    }]
    expected = [{
        'code': 'c',
        'reference product': 'foo',
        'type': 'market activity',
        'name': '',
        'location': 'RoW',
        'suppliers': [{
            'type': 'reference product',
            'location': 'GLO',
            'code': 'a',
            'name': 'first',
        }, {
            'type': 'reference product',
            'location': 'MX',
            'code': 'b',
            'name': 'second',
        }]
    }]
    apportion_suppliers_to_consumers(consumers, suppliers)
    consumers[0]['suppliers'].sort(key = lambda x: x['location'])
    expected[0]['suppliers'].sort(key = lambda x: x['location'])
    assert consumers == expected

def test_apportion_suppliers_to_consumers_no_suppliers():
    consumers = [
        generate_dataset('UCTE without France'),
    ]
    assert apportion_suppliers_to_consumers(consumers, [])

def test_apportion_suppliers_to_consumers_nonlinked_suppliers():
    consumers = [
        generate_dataset('UCTE without France'),
    ]
    suppliers = [
        generate_dataset('FR'),
        generate_dataset('DE'),
    ]
    for s in suppliers:
        s.update({'exchanges': [{'type': 'reference product'}]})
    assert apportion_suppliers_to_consumers(consumers, suppliers)

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
    expected = [{
        'type': 'skip me',
    }, {
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'location': 'CA',
        'code': 'cCA',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'location': 'MX',
        'code': 'cMX',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'type': 'transforming activity',
        'reference product': 'foo',
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
                'name': '',
            },
            {
                'code': 'cMX',
                'location': 'MX',
                'type': 'reference product',
                'name': ''
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
            'name': ''
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
        'suppliers': [{
            'code': 'cDE',
            'location': 'DE',
            'type': 'reference product',
            'name': '',
        }, {
            'code': 'cZA',
            'location': 'ZA',
            'type': 'reference product',
            'name': '',
        }]
    }]
    assert add_suppliers_to_markets(given) == expected

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
                'name': '',
            },
            {
                'code': 'cMX',
                'location': 'MX',
                'type': 'reference product',
                'name': ''
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
            'name': ''
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
