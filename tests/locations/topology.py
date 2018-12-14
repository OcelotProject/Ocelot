# -*- coding: utf-8 -*-
from ocelot.transformations.locations import topology
import pytest


def test_topology_loading():
    assert len(topology.data) > 400

def test_topology_contained():
    assert topology.contained('RU') == {'Russia (Asia)', 'Russia (Europe)', 'RU'}
    assert topology.contained('GLO')
    assert topology.contained('RoW') == set()
    # Test compatibility labels
    assert topology.contained('IAI Area 8')
    with pytest.raises(KeyError):
        topology.contained('foo')

def test_topology_contained_exclude_self():
    assert topology.contained('RU', exclude_self=True) == {'Russia (Asia)', 'Russia (Europe)'}

def test_topology_intersected():
    assert 'UN-EUROPE' in topology.intersected('DE')
    assert 'DE' in topology.intersected('DE')
    assert 'DE' not in topology.intersected('DE', exclude_self=True)
    assert 'RER w/o AT+BE+CH+DE+FR+IT' not in topology.intersected('CH')
    assert topology.intersected('GLO') == set()
    assert topology.intersected('RoW') == set()
    # Test compatibility labels
    assert topology.intersected('IAI Area 8')
    # Test new Ecoinvent 3.3 compatablility labels
    assert topology.intersected('IAI Area, Asia, without China and GCC')
    assert topology.intersected('IAI Area, Gulf Cooperation Council')
    with pytest.raises(KeyError):
        topology.intersected('foo')

def test_topology_intersects():
    assert topology.intersects('DE', 'UN-EUROPE')
    assert not topology.intersects('US', 'UN-EUROPE')

def test_topology_calls():
    assert topology('US') == topology.data['US']
    assert topology('GLO') == topology.data['__all__']
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

def test_topology_ordered_dependencies():
    given = [
        {'location': 'GLO'},
        {'location': 'CA'},
        {'location': 'Canada without Quebec'},
        {'location': 'RNA'},
        {'location': 'US'},
        {'location': 'CN'},
        {'location': 'ENTSO-E'},
        {'location': 'Europe without Switzerland'},
        {'location': 'RER'},
        {'location': 'UCTE'},
        {'location': 'RAF'},
        {'location': 'RAS'},
        {'location': 'RLA'},
        {'location': 'RME'},
        {'location': 'RoW'},
    ]
    expected = ['GLO', 'RNA', 'RER', 'RAS', 'ENTSO-E', 'CA', 'US', 'UCTE',
                'RoW', 'RME', 'RLA', 'RAF', 'Europe without Switzerland',
                'Canada without Quebec', 'CN']
    assert topology.ordered_dependencies(given) == expected

# def test_topology_tree():
#     given = [
#         # market group for electricity, low voltage, ecoinvent 3.3
#         {'location': 'GLO'},
#         {'location': 'CA'},
#         {'location': 'Canada without Quebec'},
#         {'location': 'RNA'},
#         {'location': 'US'},
#         {'location': 'CN'},
#         {'location': 'ENTSO-E'},
#         {'location': 'Europe without Switzerland'},
#         {'location': 'RER'},
#         {'location': 'UCTE'},
#         {'location': 'RAF'},
#         {'location': 'RAS'},
#         {'location': 'RLA'},
#         {'location': 'RME'},
#     ]
#     expected = {
#         'GLO': {
#             'RNA': {
#                 'CA': {'Canada without Quebec': {}},
#                 'US': {}
#             },
#             'RAF': {},
#             'RAS': {
#                 "CN": {},
#                 "RME": {}
#             },
#             'RLA': {},
#             'RER': {
#                 'ENTSO-E': {
#                     'UCTE': {}
#                 },
#                 'Europe without Switzerland': {}
#             }
#         }
#     }
#     assert topology.tree(given) == expected

# def test_topology_tree_row():
#     given = [
#         {'location': 'CA'},
#         {'location': 'GLO'},
#         {'location': 'RoW'},
#     ]
#     expected = {
#         'GLO': {
#             'CA': {},
#             'RoW': {}
#         }
#     }
#     assert topology.tree(given) == expected
#     given = [
#         {'location': 'CA'},
#         {'location': 'RoW'},
#     ]
#     expected = {
#         'CA': {},
#         'RoW': {}
#     }
#     assert topology.tree(given) == expected

# def test_topology_tree_glo():
#     given = [
#         {'location': 'CA'},
#         {'location': 'GLO'},
#     ]
#     expected = {'GLO': {'CA': {}}}
#     assert topology.tree(given) == expected

def test_topology_subtract():
    assert topology.contained('RER', subtract=('Europe without Switzerland',)) == {'CH'}
