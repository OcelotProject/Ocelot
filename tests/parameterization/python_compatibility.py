# -*- coding: utf-8 -*-
from ocelot.errors import UnparsableFormula
from ocelot.transformations.parameterization.python_compatibility import *
from copy import deepcopy
import pytest


def test_fix_math_formulas():
    bad, good = "% ^ \r\n", "e-2 ** "
    given = [{
        'name': 'a name',
        'exchanges': [{
            'formula': deepcopy(bad),
            'production volume': {'formula': deepcopy(bad)},
            'properties': [{'formula': deepcopy(bad)}]
        }],
        'parameters': [{'formula': deepcopy(bad)}]
    }]
    expected = [{
        'name': 'a name',
        'exchanges': [{
            'formula': deepcopy(good),
            'production volume': {'formula': deepcopy(good)},
            'properties': [{'formula': deepcopy(good)}]
        }],
        'parameters': [{'formula': deepcopy(good)}]
    }]
    assert fix_math_formulas(given) == expected

def test_find_if_clause():
    ds = {'name': ''}
    string = "if(T1_kW/hp_to_kW<750;T123_co_750hp;T124_co_750php)"
    expected = "((T123_co_750hp) if (T1_kW/hp_to_kW<750) else (T124_co_750php))"
    assert find_if_clause(ds, string) == expected

    string = "if(c_soil_mineral>0;c_soil_mineral*(1/r) *ef_n2o_n*n2o_n_2_n2o;0)"
    expected = "((c_soil_mineral*(1/r) *ef_n2o_n*n2o_n_2_n2o) if (c_soil_mineral>0) else (0))"
    assert find_if_clause(ds, string) == expected

def test_find_if_clause_same_value():
    ds = {'name': ''}
    string = "(euro_iiia* ep* lf*(if(ep>130;0.488;0.488))+euro_iiib* ep* lf*(if(ep>130;0.185;0.185)))/1000"
    expected = "(euro_iiia* ep* lf*((0.488))+euro_iiib* ep* lf*((0.185)))/1000"
    assert find_if_clause(ds, string) == expected


@pytest.mark.skip(reason="Current approach won't work on nested expressions")
def test_nested_if_clause():
    ds = {'name': ''}
    string = "if(condition1;if(condition2;yes;no);if(condition3;up;down))"
    expected = ("((((yes) if (condition2) else (no))) if (condition1) else "
        "(((up) if (condition3) else (down))))")
    assert find_if_clause(ds, string) == expected

def test_find_power_clause():
    ds = {'name': ''}
    string = "power(4;6)"
    expected = "((4.0)**(6.0))"
    assert find_power_clause(ds, string) == expected

def test_find_power_clause_leading_zeros():
    ds = {'name': ''}
    string = "6.6898*power(10;-05)*crown_leaf_residue + 3.2327*power(10;-05)*crown_leaf_harvest"
    expected = "6.6898*((10.0)**(-5.0))*crown_leaf_residue + 3.2327*((10.0)**(-5.0))*crown_leaf_harvest"
    assert find_power_clause(ds, string) == expected

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
