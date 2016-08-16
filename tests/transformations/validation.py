# -*- coding: utf-8 -*-
from ocelot.errors import InvalidMultioutputDataset
from ocelot.transformations.validation import check_single_output_activity
import pytest


def test_check_single_output():
    ds = {'exchanges': [{
        'type': 'reference product'
    }]}
    assert check_single_output_activity(ds)
    assert check_single_output_activity(ds) is ds

def test_no_reference_product():
    ds = {'exchanges': [{
        'type': 'to environment'
    }]}
    with pytest.raises(InvalidMultioutputDataset):
        check_single_output_activity(ds)

def test_correct_byproduct():
    ds = {'exchanges': [{
        'type': 'reference product',
    }, {
        'type': 'byproduct',
        'byproduct classification': 'waste'
    }]}
    assert check_single_output_activity(ds)

def test_wrong_byproduct():
    ds = {'exchanges': [{
        'type': 'reference product',
    }, {
        'type': 'byproduct',
        'byproduct classification': 'allocatable product'
    }]}
    with pytest.raises(InvalidMultioutputDataset):
        check_single_output_activity(ds)

def test_multiple_reference_products():
    ds = {'exchanges': [{
        'type': 'reference product',
    }, {
        'type': 'reference product',
    }]}
    with pytest.raises(InvalidMultioutputDataset):
        check_single_output_activity(ds)
