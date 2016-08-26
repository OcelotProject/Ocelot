# -*- coding: utf-8 -*-
from ocelot.transformations.parameterization.known_ecoinvent_issues import (
    fix_known_bad_formula_strings,
    fix_specific_ecoinvent_issues,
)


def test_fix_strings():
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
    assert fix_known_bad_formula_strings(data) == expected

def test_fix_specific_ecoinvent_issues():
    given = [{
        'name': 'one',
        'exchanges': [{'name': 'refinery gas', 'amount': 1}]
    }, {
        'name': 'petroleum refinery operation',
        'location': 'somewhere',
        'exchanges': [
            {'name': 'refinery gas', 'amount': 1},
            {'name': 'refinery gas', 'amount': 0},
            {'name': 'gasoline', 'amount': 0},
        ]
    }]
    expected = [{
        'name': 'one',
        'exchanges': [{'name': 'refinery gas', 'amount': 1}]
    }, {
        'name': 'petroleum refinery operation',
        'location': 'somewhere',
        'exchanges': [
            {'name': 'refinery gas', 'amount': 1},
            {'name': 'gasoline', 'amount': 0},
        ]
    }]
    assert fix_specific_ecoinvent_issues(given) == expected
