# -*- coding: utf-8 -*-
from ocelot.transformations.locations import topology
import pytest


def test_topology_loading():
    assert len(topology.data) > 400

def test_topology_contained():
    assert topology.contained('RU') == {'Russia (Asia)', 'Russia (Europe)', 'RU'}
    assert topology.contained('GLO') == set()
    assert topology.contained('RoW') == set()
    # Test compatibility labels
    assert topology.contained('IAI Area 8')
    with pytest.raises(KeyError):
        topology.contained('foo')

def test_topology_intersects():
    assert 'UN-EUROPE' in topology.intersects('DE')
    assert 'DE' in topology.intersects('DE')
    assert 'RER w/o AT+BE+CH+DE+FR+IT' not in topology.intersects('CH')
    assert topology.intersects('GLO') == set()
    assert topology.intersects('RoW') == set()
    # Test compatibility labels
    assert topology.intersects('IAI Area 8')
    # Test new Ecoinvent 3.3 compatablility labels
    assert topology.intersects('IAI Area, Asia, without China and GCC')
    assert topology.intersects('IAI Area, Gulf Cooperation Council')

    with pytest.raises(KeyError):
        topology.intersects('foo')

def test_topology_calls():
    assert topology('US') == topology.data['US']
    assert topology('GLO') == set()
    assert topology('RoW') == set()

def test_topology_overlaps():
    assert topology.overlaps([]) is None
    assert not topology.overlaps(['US', 'CH'])
    assert topology.overlaps(['US', 'NAFTA'])

def test_topology_contains():
    assert topology.contains("RER", "CH")
    assert topology.contains("CH", "CH")
    assert not topology.contains("US", "CH")
    assert topology.contains('NAFTA', 'US')
    assert topology.contains('UN-ASIA', 'Cyprus No Mans Area')
