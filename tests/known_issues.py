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
