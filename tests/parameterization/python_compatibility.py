# -*- coding: utf-8 -*-
from ocelot.errors import UnparsableFormula
from ocelot.transformations.parameterization.python_compatibility import *
import copy
import pytest


def test_fix_math_formulas():
    bad, switched = "ABS() % ^ \r\n", "abs() e-2 ** "
    data = [{
        'name': 'a name',
        'exchanges': [{'formula': copy.copy(bad)}],
        'parameters': []
    }]
    expected = copy.deepcopy(data)
    expected[0]['exchanges'][0]['formula'] = switched
    assert fix_math_formulas(data) == expected

def test_fix_math_formulas_production_volume():
    bad, switched = "ABS() % ^", "abs() e-2 **"
    data = [{
        'name': 'a name',
        'exchanges': [{
            'formula': '',
            'production volume': {'formula': copy.copy(bad)},
        }],
        'parameters': []
    }]
    expected = copy.deepcopy(data)
    expected[0]['exchanges'][0]['production volume']['formula'] = switched
    assert fix_math_formulas(data) == expected

def test_fix_math_formulas_properties():
    bad, switched = "ABS() % ^", "abs() e-2 **"
    data = [{
        'name': 'a name',
        'exchanges': [{
            'formula': '',
            'properties': [{'formula': copy.copy(bad)}]
        }],
        'parameters': []
    }]
    expected = copy.deepcopy(data)
    expected[0]['exchanges'][0]['properties'][0]['formula'] = switched
    assert fix_math_formulas(data) == expected

def test_fix_math_formulas_parameters():
    bad, switched = "ABS() % ^", "abs() e-2 **"
    data = [{
        'name': 'a name',
        'exchanges': [{'formula': ''}],
        'parameters': [{'formula': copy.copy(bad)}]
    }]
    expected = copy.deepcopy(data)
    expected[0]['parameters'][0]['formula'] = switched
    assert fix_math_formulas(data) == expected

def test_lowercase_all_parameters():
    given = [{
        'exchanges': [{
            'name': 'foo',
            'id': 1,
            'formula': "Banana * F1_cars",
            'variable': 'PINEapple',
            'production volume': {
                'variable': 'APPPPPPle',
                'formula': 'PERE'
            },
            'properties': [{
                'variable': 'GR8pe',
                'formula': 'K1W1',
            }]
        }],
        'parameters': [{
            'formula': 'cranBERRY',
            'variable': 'A * B / C2_niner'
        }]
    }]
    expected = [{
        'exchanges': [{
            'name': 'foo',
            'id': 1,
            'formula': "banana * f1_cars",
            'variable': 'pineapple',
            'production volume': {
                'variable': 'apppppple',
                'formula': 'pere'
            },
            'properties': [{
                'variable': 'gr8pe',
                'formula': 'k1w1',
            }]
        }],
        'parameters': [{
            'formula': 'cranberry',
            'variable': 'a * b / c2_niner'
        }]
    }]
    assert lowercase_all_parameters(given) == expected

# Known test cases from ecoinvent datasets

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
    assert lowercase_all_parameters(data) == expected

def test_fix_cement():
    data = [{
        'name': 'cement production, alternative constituents 6-20%',
        'location': 'nowhere',
        'exchanges': [{
            'formula': 'frogs + GGBFS',
            'variable': 'ggbfs',
        }]
    }]
    expected = [{
        'name': 'cement production, alternative constituents 6-20%',
        'location': 'nowhere',
        'exchanges': [{
            'formula': 'frogs + ggbfs',
            'variable': 'ggbfs'
        }]
    }]
    assert lowercase_all_parameters(data) == expected

def test_petroleum():
    data = [{
        'name': 'petroleum and gas production, off-shore',
        'location': 'nowhere',
        'exchanges': [{'formula': 'HPV vaccination != petroleum_APV'}]
    }]
    expected = [{
        'name': 'petroleum and gas production, off-shore',
        'location': 'nowhere',
        'exchanges': [{'formula': 'hpv vaccination != petroleum_apv'}]
    }]
    assert lowercase_all_parameters(data) == expected

def test_fix_ethylene():
    data = [{
        'name': 'ethylene glycol production',
        'location': 'nowhere',
        'exchanges': [{'formula': 'yield + fair * knight'}],
        'parameters': [{'variable': 'yield'}]
    }]
    expected = [{
        'name': 'ethylene glycol production',
        'location': 'nowhere',
        'exchanges': [{'formula': 'YIELD + fair * knight'}],
        'parameters': [{'variable': 'YIELD'}]
    }]
    assert replace_reserved_words(data) == expected

def test_get_ast_names():
    return
    with pytest.raises(UnparsableFormula):
        pass

def test_check_and_fix_formula():
    pass

def test_replace_reserved_words():
    pass

def test_delete_unparsable_formulas():
    pass
