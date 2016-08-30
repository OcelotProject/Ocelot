# -*- coding: utf-8 -*-
from ocelot.transformations.locations import topology
import pytest


def test_topology_loading():
    assert len(topology.data) > 400

def test_topology_contained():
    assert topology.contained('RU') == {'Russia (Asia)', 'Russia (Europe)'}
    assert topology.contained('GLO') is None
    # Test compatibility labels
    assert topology.contained('IAI Area 8')
    with pytest.raises(KeyError):
        topology.contained('foo')

def test_topology_intersects():
    assert 'UN-EUROPE' in topology.intersects('DE')
    assert 'RER w/o AT+BE+CH+DE+FR+IT' not in topology.intersects('CH')
    assert topology.intersects('GLO') is None
    # Test compatibility labels
    assert topology.intersects('IAI Area 8')
    with pytest.raises(KeyError):
        topology.intersects('foo')
