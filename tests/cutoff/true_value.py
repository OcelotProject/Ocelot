# -*- coding: utf-8 -*-
from ocelot.io.extract_ecospold2 import generic_extractor
from ocelot.io.validate_internal import dataset_schema
from ocelot.transformations.cutoff.allocation import choose_allocation_method
from ocelot.transformations.cutoff.economic import economic_allocation
import copy
import os
import pytest


### Test artificial cases

@pytest.fixture(scope="function")
def no_allocation(monkeypatch):
    monkeypatch.setattr(
        'ocelot.transformations.cutoff.economic.apply_allocation_factors',
        lambda x, y: (x, y)
    )

def test_true_value_allocation_factors(no_allocation):
    dataset = {'exchanges': [{
        'name': 'first',
        'type': 'reference product',
        'amount': 4,
        'properties': [{
            'name': 'price',
            'amount': 2.5
        }]
    }, {
        'name': 'second',
        'type': 'reference product',
        'amount': 10,
        'properties': [{
            'name': 'price',
            'amount': 2
        }]
    }, {
        'name': 'third',
        'type': 'biosphere',
        'amount': 30
    }]}
    obj, lst = economic_allocation(dataset)
    # Allocation by revenue; revenue is (4 * 2.5 = 10, 2 * 10 = 20) = (1/3, 2/3)
    assert [x[0] for x in lst] == [1/3, 2/3]

def test_normal_true_value_allocation():
    pass


### Test real test data

@pytest.fixture(scope="module")
def cogen():
    fp = os.path.join(os.path.dirname(__file__), "..", "data",
                      "heat-cogeneration-glo.spold")
    return generic_extractor(fp)[0]

def test_load_validate_cogeneration_dataset(cogen):
    assert dataset_schema(cogen)

def test_choice_allocation_method(cogen):
    assert choose_allocation_method(cogen) == economic_allocation

def test_allocation_function_output_valid(cogen):
    for new_ds in economic_allocation(cogen):
        assert dataset_schema(new_ds)

def test_allocate_cogeneration_dataset(cogen):
    pass
