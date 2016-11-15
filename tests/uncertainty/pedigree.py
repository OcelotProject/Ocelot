# -*- coding: utf-8 -*-
from ocelot.transformations.uncertainty.pedigree import *
import numpy as np
import pytest

apmt = adjust_pedigree_matrix_time


### Test changing pedigree matrix variance

def test_get_pedigree_variance_error():
    matrix = {
        "reliability": 1,
        "completeness": 2,
        "temporal correlation": 3,
        "geographical correlation": 4,
        "further technological correlation": 4.5,
    }
    with pytest.raises(AssertionError):
        get_pedigree_variance(matrix)

def test_get_pedigree_variance():
    matrix = {
        "reliability": 1,
        "completeness": 2,
        "temporal correlation": 3,
        "geographical correlation": 4,
        "further technological correlation": 5,
    }
    assert np.allclose(
        get_pedigree_variance(matrix),
        0.0001 + 0.002 + 0.0006 + 0.12
    )

def test_get_pedigree_variance_no_keys():
    assert get_pedigree_variance({}) == 0

def test_adjust_pedigree_matrix_time_no_pm():
    assert apmt(None, {}, None) == {}


### Test changing pedigree matrix temporal correlation

def test_get_difference_in_years():
    a = "2002-12-31"
    b = "2002-01-01"
    c = "2012-01-31"
    assert get_difference_in_years(a, b) == 0
    assert get_difference_in_years(b, a) == 0
    assert get_difference_in_years(b, c) == 10
    assert get_difference_in_years(c, a) == 10
    assert get_difference_in_years(2006, a) == 4


def test_adjust_pedigree_matrix_time():
    def ds_and_exc(current=0):
        return {'end date': '2000-01-01'}, {'pedigree matrix': {'temporal correlation': current}}

    ds, exc = ds_and_exc()
    assert apmt(ds, exc, 2000) == {'pedigree matrix': {'temporal correlation': 0}}
    assert apmt(ds, exc, "2000-01-01") == {'pedigree matrix': {'temporal correlation': 0}}

    ds, exc = ds_and_exc(3)
    assert apmt(ds, exc, 2003) == {'pedigree matrix': {'temporal correlation': 4}}
    ds, exc = ds_and_exc(3)
    assert apmt(ds, exc, 2008) == {'pedigree matrix': {'temporal correlation': 5}}

    ds, exc = ds_and_exc(2)
    assert apmt(ds, exc, 2003) == {'pedigree matrix': {'temporal correlation': 3}}
    ds, exc = ds_and_exc(2)
    assert apmt(ds, exc, 2005) == {'pedigree matrix': {'temporal correlation': 4}}
    ds, exc = ds_and_exc(2)
    assert apmt(ds, exc, 2007) == {'pedigree matrix': {'temporal correlation': 5}}

    ds, exc = ds_and_exc(1)
    assert apmt(ds, exc, 2002) == {'pedigree matrix': {'temporal correlation': 2}}
    ds, exc = ds_and_exc(1)
    assert apmt(ds, exc, 2005) == {'pedigree matrix': {'temporal correlation': 3}}
    ds, exc = ds_and_exc(1)
    assert apmt(ds, exc, 2010) == {'pedigree matrix': {'temporal correlation': 4}}
    ds, exc = ds_and_exc(1)
    assert apmt(ds, exc, 2015) == {'pedigree matrix': {'temporal correlation': 5}}
