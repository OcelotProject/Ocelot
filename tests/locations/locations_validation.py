# -*- coding: utf-8 -*-
from ocelot.errors import OverlappingMarkets
from ocelot.transformations.locations.validation import (
    check_markets_dont_overlap,
    check_single_global_dataset,
)
import pytest


def test_markets_dont_overlap():
    given =[{
        'type': 'market activity',
        'location': 'CH',
        'reference product': 'chocolate',
    }, {
        'type': 'market activity',
        'location': 'DE',
        'reference product': 'chocolate',
    }]
    assert check_markets_dont_overlap(given)

def test_markets_do_overlap():
    given =[{
        'type': 'market activity',
        'location': 'US',
        'reference product': 'blueberries',
    }, {
        'type': 'market activity',
        'location': 'NAFTA',
        'reference product': 'blueberries',
    }]
    with pytest.raises(OverlappingMarkets):
        check_markets_dont_overlap(given)
