# -*- coding: utf-8 -*-
from ocelot.errors import OverlappingActivities, MultipleGlobalDatasets
from ocelot.transformations.locations.validation import (
    # check_markets_dont_overlap,
    check_single_global_dataset,
    no_geo_duplicates,
    no_overlaps,
)
import pytest


def test_check_single_global_dataset():
    given = [{'location': 'up'}, {'location': 'down'}]
    assert check_single_global_dataset(given) is None

    with pytest.raises(MultipleGlobalDatasets):
        given = [{'location': 'GLO'}, {'location': 'GLO'}]
        check_single_global_dataset(given)

# def test_markets_dont_overlap():
#     given =[{
#         'type': 'market activity',
#         'location': 'CH',
#         'reference product': 'chocolate',
#     }, {
#         'type': 'market activity',
#         'location': 'DE',
#         'reference product': 'chocolate',
#     }]
#     assert check_markets_dont_overlap(given)

# def test_markets_do_overlap():
#     given =[{
#         'type': 'market activity',
#         'location': 'US',
#         'reference product': 'blueberries',
#     }, {
#         'type': 'market activity',
#         'location': 'NAFTA',
#         'reference product': 'blueberries',
#     }]
#     with pytest.raises(OverlappingActivities):
#         check_markets_dont_overlap(given)

def test_no_overlaps():
    @no_overlaps
    def f(consumers, suppliers):
        return True

    consumers = [{'location': 'US'}, {'location': 'CH'}]
    suppliers = []
    assert f(consumers, suppliers)
    assert f(suppliers, consumers)

    with pytest.raises(OverlappingActivities):
        consumers = [{'location': 'DE'}, {'location': 'RER'}]
        f(consumers, suppliers)

def test_no_geo_duplicates():
    @no_geo_duplicates
    def f(consumers, suppliers):
        return True

    consumers = [{'location': 'US'}, {'location': 'CH'}]
    suppliers = []
    assert f(consumers, suppliers)
    assert f(suppliers, consumers)

    with pytest.raises(ValueError):
        consumers = [
            {'location': 'US'},
            {'location': 'DE'},
            {'location': 'US'},
        ]
        f(consumers, suppliers)
