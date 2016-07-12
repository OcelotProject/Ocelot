# -*- coding: utf-8 -*-
from ocelot.data_helpers import (
    production_volume,
    reference_products_as_string,
)

### Test production_volume function

def test_production_volume_multiple():
    dataset = {'exchanges': [
        {
            'type': 'reference product',
        }, {
            'type': 'reference product',
        }
    ]}
    assert production_volume(dataset) is None

def test_production_volume_none():
    dataset = {'exchanges': []}
    assert production_volume(dataset) is None

def test_production_volume_no_amount():
    dataset = {'exchanges': [
        {
            'type': 'reference product',
            'production volume': {}
        }
    ]}
    assert production_volume(dataset) is None

def test_production_volume_keyerror():
    dataset = {'exchanges': [
        {
            'type': 'reference product',
        }
    ]}
    assert production_volume(dataset) is None

def test_production_volume():
    dataset = {'exchanges': [
        {
            'type': 'something else',
            'production volume': {
                'amount': 2
            },
        }, {
            'type': 'reference product',
            'production volume': {
                'amount': 42
            },
        }
    ]}
    assert production_volume(dataset) == 42


### Test reference_products_as_string function

def test_reference_products_none():
    dataset = {'exchanges': []}
    assert reference_products_as_string(dataset) == "None found"

def test_reference_products_single():
    dataset = {'exchanges': [{
        'type': 'reference product',
        'name': 'foo'
    }]}
    assert reference_products_as_string(dataset) == "foo"

def test_reference_products_multiple():
    dataset = {'exchanges': [
        {
            'type': 'reference product',
            'name': 'foo'
        }, {
            'type': 'reference product',
            'name': 'bar'
        }
    ]}
    assert reference_products_as_string(dataset) == "bar|foo"
