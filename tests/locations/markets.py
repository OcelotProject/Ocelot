# -*- coding: utf-8 -*-
from ocelot.transformations.locations.markets import (
    add_suppliers_to_markets,
    allocate_suppliers,
    apportion_suppliers_to_consumers,
)

def generate_dataset(location, name='foo', rp='bar'):
    return {
        'name': name,
        'reference product': rp,
        'location': location
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
        s.update({'exchanges': [{'type': 'reference product', 'l': s['location']}]})
    expected = [{
        'reference product': 'bar',
        'name': 'foo',
        'location': 'UCTE without France',
        'suppliers': [{'l': 'DE', 'type': 'reference product'}]
    }, {
        'reference product': 'bar',
        'name': 'foo',
        'location': 'RU',
        'suppliers': [{'l': 'Russia (Asia)', 'type': 'reference product'}]
    }, {
        'reference product': 'bar',
        'name': 'foo',
        'location': 'RoW',
        'suppliers': [
            {'l': 'FR', 'type': 'reference product'},
            {'l': 'MY', 'type': 'reference product'}
        ]
    }]

    apportion_suppliers_to_consumers(consumers, suppliers)
    assert consumers == expected
