# -*- coding: utf-8 -*-
from ocelot.io.extract_ecospold2 import generic_extractor
from ocelot.io.validate_internal import dataset_schema
import copy
import pytest
import os

### Test artificial cases

# def test_normal_economic_allocation():
#     pass

# def test_economic_allocation_no_price():
#     pass

# def test_economic_allocation_negative_price():
#     pass

# def test_economic_allocation_negative_amount():
#     pass

# def test_economic_allocation_zero_amount():
#     pass

# def test_economic_allocation_zero_price():
#     pass

### Test real test data

@pytest.fixture(scope="module")
def cogen():
    fp = os.path.join(os.path.dirname(__file__), "..", "data",
                      "heat-cogeneration-glo.spold")
    return generic_extractor(fp)[0]


def test_load_validate_cogeneration_dataset(cogen):
    assert dataset_schema(cogen)

def test_allocate_cogeneration_dataset(cogen):
    pass
