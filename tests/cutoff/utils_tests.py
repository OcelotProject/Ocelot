# -*- coding: utf-8 -*-
from ocelot.transformations.cutoff.utils import delete_allocation_method

def test_delete_allocation_method():
    given = {'allocation method': 'something'}
    assert delete_allocation_method(given) == [{}]

    given = {'foo': 'bar'}
    assert delete_allocation_method(given) == [{'foo': 'bar'}]
