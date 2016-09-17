# -*- coding: utf-8 -*-
from ocelot.transformations.uncertainty import *
import pytest


def test_get_uncertainty_class():
    for k, v in TYPE_MAPPING.items():
        exchange = {'uncertainty': {'type': k}}
        assert get_uncertainty_class(exchange) == v
    assert get_uncertainty_class({}) == NoUncertainty
    with pytest.raises(UnsupportedDistribution):
        assert get_uncertainty_class({'uncertainty': {'type': 'foo'}})

def test_remove_exchange_uncertainty():
    assert remove_exchange_uncertainty({}) == {}
    assert remove_exchange_uncertainty({'uncertainty': {}}) == {}

def test_scale_exchange(monkeypatch):
    """Test of underlying functionality will happen in module-level tests"""
    class Foo:
        def rescale(self, exchange, factor):
            return factor

    def get_funcertainty_class(exchange):
        return Foo()

    monkeypatch.setattr(
        'ocelot.transformations.uncertainty.get_uncertainty_class',
        get_funcertainty_class
    )
    assert scale_exchange("foo", 1) == "foo"
    assert scale_exchange("foo", 2) == 2

def test_adjust_pedigree_matrix_time(monkeypatch):
    """Test of underlying functionality will happen in module-level tests"""
    class Foo:
        def recalculate(self, exchange):
            return exchange

    def get_funcertainty_class(exchange):
        return Foo()

    def fake_func(ds, exchange, year):
        return year

    monkeypatch.setattr(
        'ocelot.transformations.uncertainty.apmt',
        fake_func
    )
    monkeypatch.setattr(
        'ocelot.transformations.uncertainty.get_uncertainty_class',
        get_funcertainty_class
    )
    assert adjust_pedigree_matrix_time(None, None, 2007) == 2007

