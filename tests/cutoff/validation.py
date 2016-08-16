# -*- coding: utf-8 -*-
from ocelot.errors import InvalidExchange
from ocelot.transformations.cutoff.validation import (valid_recycling_activity,
    valid_economic_activity,
)
import pytest



def test_recycling_activity_validation_errors():
    @valid_recycling_activity
    def f(dataset):
        return dataset

    no_byproduct = {'exchanges': [
        {
            'type': 'reference product',
            'amount': 1
        }
    ]}
    with pytest.raises(InvalidExchange):
        f(no_byproduct)

    negative_value = {'exchanges': [
        {
            'type': 'reference product',
            'amount': -1
        }
    ]}
    with pytest.raises(InvalidExchange):
        f(negative_value)

    wrong_classification = {'exchanges': [
        {
            'type': 'reference product',
            'amount': 1
        },
        {
            'type': 'byproduct',
            'byproduct classification': 'waste'
        }
    ]}
    with pytest.raises(InvalidExchange):
        f(wrong_classification)

def test_recycling_activity_validation():
    @valid_recycling_activity
    def f(dataset):
        return dataset

    correct = {'exchanges': [
        {
            'type': 'reference product',
            'amount': 1
        },
        {
            'type': 'byproduct',
            'byproduct classification': 'allocatable product'
        }
    ]}
    assert f(correct) is correct
    assert f(dataset=correct) is correct

def test_economic_activity_validation_errors():
    @valid_economic_activity
    def f(dataset):
        return dataset

    missing_price = {'exchanges': [
        {
            'type': 'reference product',
            'properties': [{
                'name': 'wrong',
            }]
        },
    ]}
    with pytest.raises(InvalidExchange):
        f(missing_price)

    no_price_amount = {'exchanges': [
        {
            'type': 'reference product',
            'properties': [{
                'name': 'price',
            }]
        },
    ]}
    with pytest.raises(InvalidExchange):
        f(no_price_amount)

def test_economic_activity_validation():
    @valid_economic_activity
    def f(dataset):
        return dataset

    data = {'exchanges': [
        {
            'type': 'reference product',
            'properties': [{
                'name': 'price',
                'amount': 1
            }]
        },
    ]}
    assert f(data) is data
    assert f(dataset=data) is data
