# -*- coding: utf-8 -*-
from ..utils import same_metadata
from ocelot.io.extract_ecospold2 import generic_extractor
from ocelot.io.validate_internal import dataset_schema
from ocelot.transformations.cutoff.allocation import choose_allocation_method
from ocelot.transformations.cutoff.wastes import recycling_allocation
from copy import deepcopy
import os
import pytest


@pytest.fixture(scope="function")
def aluminium():
    fp = os.path.join(os.path.dirname(__file__), "..", "data",
                      "treatment-aluminium.spold")
    return generic_extractor(fp)[0]

def test_load_validate_aluminium_dataset(aluminium):
    assert dataset_schema(aluminium)

def test_choice_allocation_method(aluminium):
    assert choose_allocation_method(aluminium) == recycling_allocation

def test_allocation_function_output_valid(aluminium):
    for new_ds in recycling_allocation(aluminium):
        assert dataset_schema(new_ds)

def test_recycling_allocation(aluminium, monkeypatch):
    monkeypatch.setattr(
        'ocelot.transformations.cutoff.wastes.economic_allocation',
        lambda x: x
    )
    given = deepcopy(aluminium)
    result = recycling_allocation(aluminium)

    same_metadata(given, result)
    assert given['exchanges'][1:] == result['exchanges'][1:]

    rp = given['exchanges'][0]
    assert rp['type'] == 'reference product'
    assert rp['amount'] == -1

    rp = result['exchanges'][0]
    assert rp['type'] == 'from technosphere'
    assert rp['amount'] == 1
