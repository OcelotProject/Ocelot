# -*- coding: utf-8 -*-
from ocelot.errors import OverlappingMarkets, MissingSupplier
from ocelot.transformations.locations.markets import *
from copy import deepcopy
import pytest


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
            'technology level': 'current',
            'code': 'Russia (Asia)foobar'
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
            }, {
                'type': 'reference product',
                'location': 'MY',
                'technology level': 'current',
                'code': 'MYfoobar',
            }
        ]
    }]
    apportion_suppliers_to_consumers(consumers, suppliers)
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
            },
            {
                'code': 'cMX',
                'location': 'MX',
                'technology level': 'current',
                'type': 'reference product'
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
            'location': 'FR'
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
            'type': 'reference product'
        }, {
            'code': 'cZA',
            'location': 'ZA',
            'technology level': 'current',
            'type': 'reference product'
        }
        ]
    }]
    assert add_suppliers_to_markets(given) == expected

def test_allocate_suppliers():
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
        'uncertainty': {
            'maximum': 2 / 12 * 24,
            'minimum': 2 / 12 * 24,
            'pedigree matrix': {},
            'standard deviation 95%': 0.0,
            'type': 'undefined'
        }
    }, {
        'amount': 10 / 12 * 24,
        'code': 'do',
        'name': '',
        'tag': 'intermediateExchange',
        'type': 'from technosphere',
        'unit': '',
        'uncertainty': {
            'maximum': 10 / 12 * 24,
            'minimum': 10 / 12 * 24,
            'pedigree matrix': {},
            'standard deviation 95%': 0.0,
            'type': 'undefined'
        }
    }]
    assert allocate_suppliers(deepcopy(given))[0]['exchanges'] == expected

def test_update_market_production_volumes():
    given = [{
        'name': '',
        'type': 'foo',
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
        'exchanges': [{
            'name': '',
            'type': 'reference product',
            'production volume': {'subtracted activity link volume': 15}
        }],
        'suppliers': [
            {'production volume': {'amount': 10}},
            {'production volume': {'amount': 20}},
        ]
    }]
    ds = update_market_production_volumes(given, 'foo')[0]
    assert ds['exchanges'][0]['production volume']['amount'] == 15

def test_update_market_production_volumes_negative_sum():
    given = [{
        'name': '',
        'type': 'foo',
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
