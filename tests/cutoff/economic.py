# -*- coding: utf-8 -*-
import pytest
from ocelot.transformations.cutoff.economic import economic_allocation


@pytest.fixture(scope="function")
def no_allocation(monkeypatch):
    monkeypatch.setattr(
        'ocelot.transformations.cutoff.economic.apply_allocation_factors',
        lambda x, y: (x, y)
    )


def test_economic_allocation_outputs(no_allocation):
    dataset = {
        'exchanges': [{
            'type': 'reference product',
            'name': 'foo',
            'amount': 2,
            'properties': [{
                'name': 'price',
                'amount': 14
            }]
        }]
    }
    expected = {
        'type': 'reference product',
        'name': 'foo',
        'amount': 2,
        'properties': [{
            'name': 'price',
            'amount': 14
        }]
    }
    obj, lst = economic_allocation(dataset)
    assert obj is dataset
    assert list(lst) == [(1, expected)]

def test_normal_economic_allocation():
    pass

def test_economic_allocation_negative_price():
    pass

def test_economic_allocation_negative_amount():
    pass

def test_economic_allocation_zero_amount():
    pass

def test_economic_allocation_zero_price():
    pass
