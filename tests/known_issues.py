# -*- coding: utf-8 -*-
from ocelot.transformations.known_ecoinvent_issues import *
import copy


def test_fix_formulas():
    bad, switched = "ABS() % ^", "abs() e-2 **"
    data = [{
        'exchanges': [{'formula': copy.copy(bad)}],
        'parameters': []
    }]
    expected = copy.deepcopy(data)
    expected[0]['exchanges'][0]['formula'] = switched
    assert fix_formulas(data) == expected

def test_fix_formulas_production_volume():
    bad, switched = "ABS() % ^", "abs() e-2 **"
    data = [{
        'exchanges': [{
            'formula': '',
            'production volume': {'formula': copy.copy(bad)},
        }],
        'parameters': []
    }]
    expected = copy.deepcopy(data)
    expected[0]['exchanges'][0]['production volume']['formula'] = switched
    assert fix_formulas(data) == expected

def test_fix_formulas_properties():
    bad, switched = "ABS() % ^", "abs() e-2 **"
    data = [{
        'exchanges': [{
            'formula': '',
            'properties': [{'formula': copy.copy(bad)}]
        }],
        'parameters': []
    }]
    expected = copy.deepcopy(data)
    expected[0]['exchanges'][0]['properties'][0]['formula'] = switched
    assert fix_formulas(data) == expected

def test_fix_formulas_parameters():
    bad, switched = "ABS() % ^", "abs() e-2 **"
    data = [{
        'exchanges': [{'formula': ''}],
        'parameters': [{'formula': copy.copy(bad)}]
    }]
    expected = copy.deepcopy(data)
    expected[0]['parameters'][0]['formula'] = switched
    assert fix_formulas(data) == expected

def test_fix_clinker_pv():
    data = [{
        'name': 'clinker production',
        'location': 'nowhere',
        'exchanges': [{'production volume': {
            'formula': '1 * clinker_PV / everything',
            'variable': 'clinker_PV'
    }}]}]
    expected = [{
        'name': 'clinker production',
        'location': 'nowhere',
        'exchanges': [{'production volume': {
            'formula': '1 * clinker_pv / everything',
            'variable': 'clinker_pv'
    }}]}]
    assert fix_clinker_pv_variable_name(data) == expected

def test_fix_cement():
    data = [{
        'name': 'cement production, alternative constituents 6-20%',
        'location': 'nowhere',
        'exchanges': [{
            'formula': 'frogs + ggbfs',
            'variable': 'ggbfs',
        }]
    }]
    expected = [{
        'name': 'cement production, alternative constituents 6-20%',
        'location': 'nowhere',
        'exchanges': [{
            'formula': 'frogs + GGBFS',
            'variable': 'GGBFS'
        }]
    }]
    assert fix_cement_production_variable_name(data) == expected

def test_fix_ethylene():
    data = [{
        'name': 'ethylene glycol production',
        'location': 'nowhere',
        'exchanges': [{'formula': 'yield fair knight'}],
        'parameters': [{'variable': 'yield'}]
    }]
    expected = [{
        'name': 'ethylene glycol production',
        'location': 'nowhere',
        'exchanges': [{'formula': 'Yield fair knight'}],
        'parameters': [{'variable': 'Yield'}]
    }]
    assert fix_ethylene_glycol_uses_yield(data) == expected

def test_petroleum():
    data = [{
        'name': 'petroleum and gas production, off-shore',
        'location': 'nowhere',
        'exchanges': [{'formula': 'HPV vaccination != petroleum_APV'}]
    }]
    expected = [{
        'name': 'petroleum and gas production, off-shore',
        'location': 'nowhere',
        'exchanges': [{'formula': 'HPV vaccination != petroleum_apv'}]
    }]
    assert fix_offshore_petroleum_variable_name(data) == expected

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
