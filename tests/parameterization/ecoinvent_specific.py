# -*- coding: utf-8 -*-
from ocelot.transformations.parameterization.known_ecoinvent_issues import fix_benzene_chlorination_unit


def test_fix_benzene():
    data = [{
        'name': 'benzene chlorination',
        'location': 'nowhere',
        'exchanges': [{'production volume': {
            'formula': '1 * UnitConversion(152000000, \'pound avoirdupois\', \'kg\')',
    }}]}]
    expected = [{
        'name': 'benzene chlorination',
        'location': 'nowhere',
        'exchanges': [{'production volume': {
            'formula': '1 * 68949040.24',
    }}]}]
    assert fix_benzene_chlorination_unit(data) == expected
