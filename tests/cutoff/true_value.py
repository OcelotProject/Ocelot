# -*- coding: utf-8 -*-
from ocelot.io.extract_ecospold2 import generic_extractor
from ocelot.io.validate_internal import dataset_schema
import copy
import pytest
import os


@pytest.fixture(scope="module")
def cogen():
    fp = os.path.join(os.path.dirname(__file__), "..", "data",
                      "heat-cogeneration-glo.spold")
    return generic_extractor(fp)[0]


def test_load_validate_cogeneration_dataset(cogen):
    assert dataset_schema(cogen)
