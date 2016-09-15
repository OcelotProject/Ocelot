# -*- coding: utf-8 -*-
from ocelot.errors import IdenticalDatasets
from ocelot.transformations.identifying import add_unique_codes
import hashlib
import pytest


def test_add_unique_codes():
    given = [{
        'name': 'apple',
        'reference product': 'pear',
        'unit': 'cherry',
        'location': 'lemon',
        'start date': 'berry',
        'end date': 'banana'
    }]
    expected = [{
        'name': 'apple',
        'reference product': 'pear',
        'unit': 'cherry',
        'location': 'lemon',
        'start date': 'berry',
        'end date': 'banana',
        'code': hashlib.md5(
            'applepearcherrylemonberrybanana'.encode('utf-8')
        ).hexdigest()
    }]
    assert add_unique_codes(given) == expected

def test_add_unique_codes_missing_fields():
    given = [{
        'name': 'foo'
    }]
    expected = [{
        'name': 'foo',
        'code': hashlib.md5('foo'.encode('utf-8')).hexdigest()
    }]
    assert add_unique_codes(given) == expected

def test_add_unique_codes_error():
    given = [
        {'name': 'foo'},
        {'name': 'foo'},
    ]
    with pytest.raises(IdenticalDatasets):
        add_unique_codes(given)

