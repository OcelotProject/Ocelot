# -*- coding: utf-8 -*-
from collections import defaultdict
from ocelot.transformations.locations import topology
from ocelot.transformations.locations._topology import Topology
import pytest


SWISS_FACE = list(topology('CH'))[0]

def different_size_proxy(face):
    if face == SWISS_FACE:
        return 1e6
    else:
        return 1


def test_topology_loading():
    assert len(topology.data) > 400
    assert '__all__' not in topology.data
    assert 'GLO' in topology.data

def test_topology_contained():
    assert topology.contained('RU') == {'Russia (Asia)', 'Russia (Europe)', 'RU'}
    # Test compatibility labels
    assert len(topology.contained('GLO')) > 400
    assert topology.contained('IAI Area 8')
    with pytest.raises(KeyError):
        topology.contained('foo')

def test_topology_contained_exclude_self():
    assert topology.contained('RU', exclude_self=True) == {'Russia (Asia)', 'Russia (Europe)'}

def test_topology_contained_glo_always_contains_row():
    assert 'RoW' in topology.contained('GLO')
    resolved = topology.resolve_row(['CH'])
    assert 'RoW' in topology.contained('GLO', resolved_row=resolved)

    assert 'RoW' not in topology.contained('GLO', subtract=['CN'])
    resolved = topology.resolve_row(['CH'])
    assert 'RoW' not in topology.contained('GLO', resolved_row=resolved, subtract=['CN'])

def test_topology_contained_glo_exclude_self():
    assert 'GLO' in topology.contained('GLO', exclude_self=False)
    assert 'GLO' not in topology.contained('GLO', exclude_self=True)

def test_topology_contained_glo_subtract():
    assert 'GLO' not in topology.contained('GLO', subtract=['CH'])
    assert 'CH' not in topology.contained('GLO', subtract=['CH'])

def test_topology_contained_pass_set():
    faces = set.union(topology('CH'), topology('DE'))
    assert 'CH' in topology.contained(faces)
    assert 'CH' in topology.contained(faces, True)
    assert 'CH' in topology.contained(faces, True, subtract=['DE'])

def test_topology_contained_row():
    assert topology.contained('RoW') == set()
    resolved = topology.resolve_row(['CH'])
    assert 'CH' not in topology.contained('RoW', resolved_row=resolved)

def test_topology_contained_row_in_result():
    assert 'RoW' in topology.contained('RoW', resolved_row=topology.resolve_row(['CH']))
    assert 'RoW' not in topology.contained('RoW', resolved_row=topology.resolve_row(['CH']), exclude_self=True)
    assert 'RoW' not in topology.contained('RoW', resolved_row=set())
    assert 'RoW' not in topology.contained('RoW')

def test_topology_contained_empty_set():
    assert not topology.contained('RoW', resolved_row=set())
    assert 'RoW' not in topology.contained('CH', resolved_row=set())
    assert 'RoW' not in topology.contained('GLO', resolved_row=set())
    assert not topology.contained("GLO", subtract=['GLO'])
    assert not topology.contained("CH", subtract=['CH'])
    assert not topology.contained("RoW", subtract=['CH'])

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
    assert topology('GLO') == topology.data['GLO']
    assert topology('RoW') == set()

def test_topology_overlaps():
    assert topology.overlaps([]) is None
    assert not topology.overlaps(['US', 'CH'])
    assert topology.overlaps(['US', 'NAFTA'])

def test_tc():
    assert topology.contains("RER", "CH")
    assert topology.contains("CH", "CH")
    assert not topology.contains("US", "CH")
    assert topology.contains('NAFTA', 'US')
    assert topology.contains('UN-ASIA', 'Cyprus No Mans Area')

def test_tc_glo():
    assert topology.contains("GLO", "CH")
    assert topology.contains("GLO", "GLO")

def test_tc_glo_row():
    assert topology.contains("GLO", "RoW")
    assert not topology.contains("GLO", "RoW", subtract=['CH'])
    assert topology.contains("GLO", "RoW", subtract=[])

def test_tc_row_row():
    assert not topology.contains("RoW", "RoW")

def test_tc_resolved_row_row():
    resolved = topology.resolve_row(['DE'])
    assert not topology.contains("RoW", "RoW", resolved_row=resolved)

def test_tc_row_resolved_row():
    resolved = topology.resolve_row(['DE'])
    assert not topology.contains("RoW", resolved)

def test_tc_resolved_row_resolved_row():
    resolved = topology.resolve_row(['DE'])
    resolved_two = topology.resolve_row(['WEU'])
    assert topology.contains("RoW", resolved_two, resolved_row=resolved)
    assert not topology.contains("RoW", resolved, resolved_row=resolved_two)

def test_tc_parent_row():
    assert not topology.contains("RoW", "CH")

    resolved = topology.resolve_row(['DE'])
    assert topology.contains("RoW", "CH", resolved_row=resolved)

def test_tc_parent_row_with_subtract():
    assert not topology.contains(
        "RoW", "CH",
        subtract=['RER'],
        resolved_row=topology.resolve_row(['MY'])
    )

def test_tc_child_row():
    assert topology.contains("GLO", "RoW")
    assert not topology.contains("WEU", "RoW")

    resolved = topology.resolve_row(['DE', 'FR'])
    assert not topology.contains("WEU", resolved)
    assert topology.contains("GLO", resolved)

def test_topology_contains_subtract():
    assert topology.contains('WEU', 'CH', subtract=['FR'])
    assert not topology.contains('WEU', 'CH', subtract=['CH'])

def test_tc_empty_set():
    assert not topology.contains(set(), 'CH')
    assert not topology.contains('CH', set())
    assert not topology.contains(set(), 'GLO')
    assert not topology.contains('GLO', set())
    assert not topology.contains(set(), 'RoW')
    assert not topology.contains('RoW', set())
    resolved = topology.resolve_row(['DE'])
    assert not topology.contains(set(), 'RoW', resolved_row=resolved)
    assert not topology.contains('RoW', set(), resolved_row=resolved)

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
    expected = ['GLO', 'RAS', 'RER', 'Europe without Switzerland', 'RNA',
                'ENTSO-E', 'RLA', 'CA', 'US', 'Canada without Quebec', 'UCTE',
                'RME', 'RAF', 'CN', 'RoW']
    assert topology.ordered_dependencies(given) == expected

def test_topology_ordered_dependencies_row_unresolved():
    given = [
        {'location': 'GLO'},
        {'location': 'CA'},
        {'location': 'RER'},
        {'location': 'RoW'},
    ]
    expected = ['GLO', 'RER', 'CA', 'RoW']
    assert topology.ordered_dependencies(given) == expected

def test_topology_ordered_dependencies_row_resolved():
    resolved = topology.resolve_row(['RAS', 'RNA', 'RER'])
    given = [
        {'location': 'GLO'},
        {'location': 'CA'},
        {'location': 'RER'},
        {'location': 'RoW'},
    ]
    expected = ['GLO', 'RoW', 'RER', 'CA']
    assert topology.ordered_dependencies(given, resolved) == expected

def test_topology_ordered_dependencies_different_size_proxy():
    given = [
        {'location': 'GLO'},
        {'location': 'CA'},
        {'location': 'CH'},
    ]
    expected = ['GLO', 'CA', 'CH']
    assert topology.ordered_dependencies(given) == expected

    t2 = Topology(different_size_proxy)
    given = [
        {'location': 'GLO'},
        {'location': 'CA'},
        {'location': 'CH'},
    ]
    expected = ['GLO', 'CH', 'CA']
    assert t2.ordered_dependencies(given) == expected

def test_topology_subtract():
    assert topology.contained('RER', subtract=('Europe without Switzerland',)) == {'CH'}
