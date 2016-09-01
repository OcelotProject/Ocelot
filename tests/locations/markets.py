# -*- coding: utf-8 -*-
from ocelot.transformations.locations.markets import *
from copy import deepcopy
import pytest


def generate_dataset(location, name='foo', rp='bar'):
    return {
        'name': name,
        'reference product': rp,
        'location': location,
        'code': location + name + rp
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
        'location': 'UCTE without France',
        'suppliers': [{
            'type': 'reference product',
            'location': 'DE',
            'code': 'DEfoobar',
        }]
    }, {
        'code': 'RUfoobar',
        'reference product': 'bar',
        'name': 'foo',
        'location': 'RU',
        'suppliers': [{
            'type': 'reference product',
            'location': 'Russia (Asia)',
            'code': 'Russia (Asia)foobar'
        }]
    }, {
        'code': 'RoWfoobar',
        'reference product': 'bar',
        'name': 'foo',
        'location': 'RoW',
        'suppliers': [
            {
                'type': 'reference product',
                'location': 'FR',
                'code': 'FRfoobar',
            }, {
                'type': 'reference product',
                'location': 'MY',
                'code': 'MYfoobar',
            }
        ]
    }]

    apportion_suppliers_to_consumers(consumers, suppliers)
    assert consumers == expected

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
        'code': 'cBR',
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'location': 'BR',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cNAFTA',
        'type': 'market activity',
        'reference product': 'foo',
        'name': '',
        'location': 'NAFTA',
    }, {
        'code': 'cGLO',
        'type': 'market activity',
        'reference product': 'foo',
        'name': '',
        'location': 'GLO',
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
        'location': 'BR',
        'code': 'cBR',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'type': 'market activity',
        'reference product': 'foo',
        'name': '',
        'location': 'NAFTA',
        'code': 'cNAFTA',
        'suppliers': [
            {'code': 'cCA', 'location': 'CA', 'type': 'reference product'},
            {'code': 'cMX', 'location': 'MX', 'type': 'reference product'}
        ]
    }, {
        'type': 'market activity',
        'reference product': 'foo',
        'name': '',
        'location': 'GLO',
        'code': 'cGLO',
        'suppliers': [{
            'code': 'cBR',
            'type': 'reference product',
            'location': 'BR'
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
            'type': 'reference product'
        }, {
            'code': 'cZA',
            'location': 'ZA',
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

def test_link_consumers_to_markets():
    given = [{
        'type': 'market activity',
        'reference product': 'cheese',
        'location': 'RER',
        'code': 'Made in the EU',
        'exchanges': [],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'location': 'BR',
        'code': 'olympics',
        'exchanges': [],
    }, {
        'type': 'market group',
        'location': 'BR',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese'
        }]
    }, {
        'type': 'transforming activity',
        'location': 'DE',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese'
        }, {
            'type': 'from technosphere',
            'name': 'cheese',
            'code': 'already here',
        }, {
            'type': 'from technosphere',
            'name': 'cheese',
            'activity link': 'skip me too',
        }, {
            'type': 'something else',
            'name': 'cheese',
        }]
    }]
    expected = [{
        'type': 'market activity',
        'reference product': 'cheese',
        'location': 'RER',
        'code': 'Made in the EU',
        'exchanges': [],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'location': 'BR',
        'code': 'olympics',
        'exchanges': [],
    }, {
        'type': 'market group',
        'location': 'BR',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese',
            'code': 'olympics',
        }]
    }, {
        'type': 'transforming activity',
        'location': 'DE',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese',
            'code': 'Made in the EU',
        }, {
            'type': 'from technosphere',
            'name': 'cheese',
            'code': 'already here',
        }, {
            'type': 'from technosphere',
            'name': 'cheese',
            'activity link': 'skip me too',
        }, {
            'type': 'something else',
            'name': 'cheese',
        }]
    }]
    assert link_consumers_to_markets(given) == expected
