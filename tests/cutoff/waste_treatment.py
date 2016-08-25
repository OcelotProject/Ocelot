# -*- coding: utf-8 -*-
from ..utils import same_metadata
from ocelot.io.extract_ecospold2 import generic_extractor
from ocelot.io.validate_internal import dataset_schema
from ocelot.transformations.cutoff.allocation import choose_allocation_method
from ocelot.transformations.cutoff.wastes import waste_treatment_allocation
import os
import pytest


### Test real test data

@pytest.fixture(scope="function")
def paper():
    fp = os.path.join(os.path.dirname(__file__), "..", "data",
                      "treatment-waste-graphical-paper.spold")
    return generic_extractor(fp)[0]

def test_load_validate_paper_dataset(paper):
    assert dataset_schema(paper)

def test_choice_allocation_method(paper):
    assert choose_allocation_method(paper) == waste_treatment_allocation

def test_allocation_function_output_valid(paper):
    for new_ds in waste_treatment_allocation(paper):
        assert dataset_schema(new_ds)

def test_allocate_paper_dataset_treatment_ds(paper):
    treatment, electricity, heat = waste_treatment_allocation(paper)
    same_metadata(treatment, paper)
    treatment_rp = treatment['exchanges'][0]
    assert treatment_rp['name'] == 'waste graphical paper'
    assert treatment_rp['type'] == 'reference product'
    assert treatment_rp['amount'] == -1

    first_dropped = treatment['exchanges'][1]
    assert first_dropped['name'] == 'electricity, for reuse in municipal waste incineration only'
    assert first_dropped['type'] == 'dropped product'
    assert first_dropped['amount'] == 0

    second_dropped = treatment['exchanges'][2]
    assert second_dropped['name'] == 'heat, for reuse in municipal waste incineration only'
    assert second_dropped['type'] == 'dropped product'
    assert second_dropped['amount'] == 0

    second_dropped = treatment['exchanges'][2]
    assert second_dropped['name'] == 'heat, for reuse in municipal waste incineration only'
    assert second_dropped['type'] == 'dropped product'
    assert second_dropped['amount'] == 0

    assert len(treatment['exchanges']) == 7
    assert treatment['exchanges'][4]['amount'] == 0.14823

def test_allocate_paper_dataset_electricity_ds(paper):
    treatment, electricity, heat = waste_treatment_allocation(paper)
    same_metadata(electricity, paper)
    assert len(electricity['exchanges']) == 1

    rp = electricity['exchanges'][0]
    assert rp['name'] == 'electricity, for reuse in municipal waste incineration only'
    assert rp['type'] == 'reference product'
    assert rp['amount'] == 1

def test_allocate_paper_dataset_heat_ds(paper):
    treatment, electricity, heat = waste_treatment_allocation(paper)
    same_metadata(heat, paper)
    assert len(heat['exchanges']) == 1

    rp = heat['exchanges'][0]
    assert rp['name'] == 'heat, for reuse in municipal waste incineration only'
    assert rp['type'] == 'reference product'
    assert rp['amount'] == 1
