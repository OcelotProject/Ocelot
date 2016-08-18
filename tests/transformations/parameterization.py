# -*- coding: utf-8 -*-
from ocelot.transformations.parameterization import *
from ocelot.errors import ParameterizationError
import pytest


def test_parameter_names_are_unique():
    data = [{'parameters': [
        {
            'name': 'foo',
            'variable': 'bar'
        }, {
            'name': 'foo',
            'variable': 'baz'
        }
    ]}]
    assert parameter_names_are_unique(data)


def test_parameter_names_are_unique_error():
    data = [{'parameters': [
        {
            'variable': 'foo'
        }, {
            'variable': 'foo'
        }
    ]}]
    with pytest.raises(ParameterizationError):
        parameter_names_are_unique(data)


@pytest.fixture(scope="function")
def parameterized_ds():
    return {
        'exchanges': [{
            'amount': 3.1415926535,
            'variable': 'pie',
            'production volume': {  # Nonsensical but should work
                'variable': 'number_blueberries',
                'amount': 42
            },
            'properties': [{
                'variable': 'blueberry_volume',
                'amount': 17
            }]
        }, {
            'variable': 'circle',
            'formula': 'pie * radius ** 2',
            'properties': [{
                'variable': 'radius',
                'formula': 'blueberry_size * number_blueberries'
            }]
        }],
        'parameters': [{
            'variable': 'blueberry_size',
            'formula': 'blueberry_density * blueberry_volume'
        }, {
            'variable': 'blueberry_density',
            'amount': 1
        }]
    }

def test_iterate_all_parameters(parameterized_ds):
    generator = iterate_all_parameters(parameterized_ds)
    assert next(generator) == parameterized_ds['exchanges'][0]
    assert next(generator) == parameterized_ds['exchanges'][0]['production volume']
    assert next(generator) == parameterized_ds['exchanges'][0]['properties'][0]
    assert next(generator) == parameterized_ds['exchanges'][1]
    assert next(generator) == parameterized_ds['exchanges'][1]['properties'][0]
    assert next(generator) == parameterized_ds['parameters'][0]
    assert next(generator) == parameterized_ds['parameters'][1]

def test_get_exchange_reference():
    uuid = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    ref = "Ref('{}')".format(uuid)
    formula = "blah blah + woo woo * {}".format(ref)
    bigger = formula + "|" + formula
    assert list(get_exchange_reference(formula)) == [(ref, uuid)]
    assert list(get_exchange_reference(bigger)) == [(ref, uuid), (ref, uuid)]
    assert not get_production_volume_reference(bigger)

def test_get_pv_reference():
    uuid = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    ref = "Ref('{}', 'ProductionVolume')".format(uuid)
    formula = "blah blah + woo woo * {}".format(ref)
    bigger = formula + "|" + formula
    assert list(get_production_volume_reference(formula)) == [(ref, uuid)]
    assert list(get_production_volume_reference(bigger)) == [(ref, uuid), (ref, uuid)]
    assert not get_exchange_reference(bigger)

def test_find_exchange_by_id():
    fake = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    real = '11111111-2222-3333-4444-555555555555'
    ds = {'exchanges': [{
        'id': 'not here',
        'name': "no!!!"
    }, {
        'id': real,
        'name': "find me"
    }]}
    found = {'id': real, 'name': "find me"}
    assert find_exchange_or_parameter_by_id(ds, real) == found
    with pytest.raises(ValueError):
        find_exchange_or_parameter_by_id(ds, fake)

def test_find_parameter_by_id():
    fake = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    real = '11111111-2222-3333-4444-555555555555'
    ds = {
        'exchanges': [],
        'parameters': [{
            'id': 'not here',
            'name': "no!!!"
        }, {
            'id': real,
            'name': "find me"
        }]
    }
    found = {'id': real, 'name': "find me"}
    assert find_exchange_or_parameter_by_id(ds, real) == found
    with pytest.raises(ValueError):
        find_exchange_or_parameter_by_id(ds, fake)

def test_find_pv_by_id():
    fake = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    real = '11111111-2222-3333-4444-555555555555'
    ds = {'exchanges': [{
        'id': 'not here',
        'name': "no!!!"
    }, {
        'id': real,
        'name': "find me",
        'production volume': 'you found me!'
    }]}
    assert find_production_volume_by_id(ds, real) == 'you found me!'
    with pytest.raises(ValueError):
        find_production_volume_by_id(ds, fake)

def test_find_pv_must_have_pv():
    real = '11111111-2222-3333-4444-555555555555'
    ds = {'exchanges': [{
        'id': real,
        'name': "find me",
    }]}
    with pytest.raises(ValueError):
        find_production_volume_by_id(ds, real)

# def test_replace_implicit_references():
#     u1 = '11111111-2222-3333-4444-555555555555'
#     u2 = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'

#     - Replace in parameter
#     - Replace in PV
#     - Replace in exchange

#     - New variable name
#     - Old variable name

#     - Multiple refs to same parameter

#     input_ds = [{
#         'exchanges': [{
#             'id': '11111111-2222-3333-4444-555555555555'
#             'amount': 2,
#             'production volume': {'amount': 4},
#             'formula': "shouldn't change"
#         }, {


#         }],
#         'parameters': [{
#             'id': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
#             'amount': 6
#         }, {


#         }]
#     }]

#     ref = "Ref('{}', 'ProductionVolume')".format(uuid)
#     formula = "blah blah + woo woo * {}".format(ref)
#     bigger = formula + "|" + formula
#     assert list(get_production_volume_reference(formula)) == [(ref, uuid)]
#     assert list(get_production_volume_reference(bigger)) == [(ref, uuid), (ref, uuid)]
#     assert not get_exchange_reference(bigger)
