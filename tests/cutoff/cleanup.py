# -*- coding: utf-8 -*-
from ocelot.transformations.cutoff.cleanup import (
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

