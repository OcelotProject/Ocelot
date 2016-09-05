# -*- coding: utf-8 -*-
from ocelot.transformations.cutoff.cleanup import (
    drop_rp_activity_links,
    drop_zero_amount_activity_links,
    remove_consequential_exchanges,
)


def test_remove_consequential_exchanges():
    given = [{
        'name': 'a name',
        'exchanges': [{
            'name': 'exchange 1',
            'amount': 1,
            'properties': [{'name': 'consequential', 'amount': 1}]
        }, {
            'name': 'exchange 2',
            'amount': 1,
            'properties': [{'name': 'consequential', 'amount': -1}]
        }, {
            'name': 'exchange 3',
            'amount': 1,
            'properties': [{'name': 'inconsequential', 'amount': 1}]
        }]
    }]
    expected = [{
        'name': 'a name',
        'exchanges': [{
            'name': 'exchange 2',
            'amount': 1,
            'properties': [{'name': 'consequential', 'amount': -1}]
        }, {
            'name': 'exchange 3',
            'amount': 1,
            'properties': [{'name': 'inconsequential', 'amount': 1}]
        }]
    }]
    assert remove_consequential_exchanges(given) == expected

def test_drop_rp_activity_links_rp():
    given = [{
        'name': 'a name',
        'exchanges': [{
            'type': 'not reference product',
            'activity link': 'keep me'
        }, {
            'type': 'reference product',
            'activity link': 'delete me',
            'name': 'something for logging'
        }]
    }]
    expected = [{
        'name': 'a name',
        'exchanges': [{
            'type': 'not reference product',
            'activity link': 'keep me'
        }, {
            'type': 'reference product',
            'name': 'something for logging'
        }]
    }]
    assert drop_rp_activity_links(given) == expected

def test_drop_rp_activity_links_dropped_product():
    given = [{
        'name': 'a name',
        'exchanges': [{
            'type': 'not reference product',
            'activity link': 'keep me'
        }, {
            'type': 'dropped product',
            'activity link': 'delete me',
            'name': 'something for logging'
        }]
    }]
    expected = [{
        'name': 'a name',
        'exchanges': [{
            'type': 'not reference product',
            'activity link': 'keep me'
        }, {
            'type': 'dropped product',
            'name': 'something for logging'
        }]
    }]
    assert drop_rp_activity_links(given) == expected

def test_drop_zero_amount_activity_links():
    given = [{
        'name': 'a name',
        'exchanges': [{
            'type': 'foo',
            'amount': 1,
            'activity link': 'keep me'
        }, {
            'type': 'foo',
            'amount': 0,
            'activity link': 'delete me',
            'name': 'something for logging'
        }]
    }]
    expected = [{
        'name': 'a name',
        'exchanges': [{
            'type': 'foo',
            'amount': 1,
            'activity link': 'keep me'
        }, {
            'type': 'foo',
            'amount': 0,
            'name': 'something for logging'
        }]
    }]
    assert drop_zero_amount_activity_links(given) == expected
