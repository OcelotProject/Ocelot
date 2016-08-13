# -*- coding: utf-8 -*-
from ocelot.transformations.utils import *


def test_allocatable_production():
    exchanges = [
        {'type': 'reference product'},
        {'type': 'not reference product'},
        {'type': 'byproduct', 'byproduct classification': 'allocatable'},
        {'type': 'byproduct', 'byproduct classification': 'cat'},
        {'type': 'byproduct', 'byproduct classification': 'allocatable'},
    ]
    dataset = {'exchanges': exchanges}
    for x, y in zip(allocatable_production(dataset), exchanges[0:5:2]):
        assert x == y
    assert len(list(allocatable_production(dataset))) == 3
