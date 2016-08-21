# -*- coding: utf-8 -*-
from ocelot.transformations.parameterization.implicit_references import *
import pytest


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

def test_replace_implicit_references():
    input_ds = [{
        'name': 'always the same',
        'exchanges': [{
            # An exchange that doesn't change
            'id': '11111111-2222-3333-4444-555555555555',
            'amount': 2,
            'production volume': {'amount': 4},
            'formula': "shouldn't change"
        }, {
            # A referenced exchange with a variable name
            'id': '10eb760b-d963-4438-a21b-4dd631926549',
            'variable': 'existing_exchange_variable',
            'production volume': {
                # A PV with a reference formula
                'formula': "Ref('b8f77151-0ddb-4d82-9c64-e46452d25ba3', 'ProductionVolume')"
            }
        }, {
            # A referenced exchange without a variable name
            'id': 'b8f77151-0ddb-4d82-9c64-e46452d25ba3',
            'amount': 10,
            'formula': "Ref('9d1f2bec-9768-4ad8-a254-f20e2401c480')",
            'production volume': {
                # A referenced PV with a variable name
                'amount': 5,
                'variable': 'existing_pv_variable'
            }
        }, {
            # An exchange with a reference formula
            'id': '5e4434c6-bff3-4575-8c92-5eac120d7378',
            'formula': "Ref('10eb760b-d963-4438-a21b-4dd631926549')",
            'production volume': {
                # A referenced PV without a variable name
                'amount': 8
            }
        }, {
            'id': '64d0d809-0164-4ea8-abc2-b737584d938e',
            'formula': "Ref('6e4c1ae5-ebbc-4845-8fa8-c5a00402ce11')",
        }],
        'parameters': [{
            # A parameter that doesn't change
            'id': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
            'amount': 6
        }, {
            # A referenced parameter with a variable name
            'id': '9d1f2bec-9768-4ad8-a254-f20e2401c480',
            'variable': 'existing_parameter_variable',
        }, {
            # A referenced parameter without a variable name
            'id': '6e4c1ae5-ebbc-4845-8fa8-c5a00402ce11',
        }, {
            # A parameter with a reference formula
            'id': 'd6896b62-c249-4cd8-915a-12c0682b2e52',
            'formula': "Ref('6e4c1ae5-ebbc-4845-8fa8-c5a00402ce11')"
        }, {
            # A PV reference
            'id': '57c91112-b260-4d14-bc95-0d2a0c4fc039',
            'formula': "Ref('b8f77151-0ddb-4d82-9c64-e46452d25ba3', 'ProductionVolume')"
        }, {
            'id': '8c44da48-2d7a-4b39-b203-03544bfbd518',
            'formula': "Ref('5e4434c6-bff3-4575-8c92-5eac120d7378', 'ProductionVolume')"
        }]
    }]
    expected = [{
        'name': 'always the same',
        'exchanges': [{
            # Doesn't change
            'amount': 2,
            'formula': "shouldn't change",
            'id': '11111111-2222-3333-4444-555555555555',
            'production volume': {'amount': 4}
        }, {
            # Referenced but doesn't change because variable
            # name already exists
            'id': '10eb760b-d963-4438-a21b-4dd631926549',
            'production volume': {
                # Substituted with reference to next exchange PV
                'formula': 'existing_pv_variable'
            },
            'variable': 'existing_exchange_variable'
        }, {
            'amount': 10,
            # Replaced with ref to parameter
            'formula': 'existing_parameter_variable',
            'id': 'b8f77151-0ddb-4d82-9c64-e46452d25ba3',
            'production volume': {
                'amount': 5,
                'variable': 'existing_pv_variable'
            }
        }, {
            # Reference to exchange substituted
            'formula': 'existing_exchange_variable',
            'id': '5e4434c6-bff3-4575-8c92-5eac120d7378',
            'production volume': {
                'amount': 8,
                # Variable name generated
                'variable': 'ref_pv_replacement_5e4434c6bff345758c925eac120d7378'
            }
        }, {
            # Second reference to this id
            'formula': 'ref_replacement_6e4c1ae5ebbc48458fa8c5a00402ce11',
            'id': '64d0d809-0164-4ea8-abc2-b737584d938e'
    }],
    'parameters': [{
            # Doesn't change
            'amount': 6,
            'id': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
        }, {
            'id': '9d1f2bec-9768-4ad8-a254-f20e2401c480',
            'variable': 'existing_parameter_variable'
        }, {
            'id': '6e4c1ae5-ebbc-4845-8fa8-c5a00402ce11',
            # Variable name generated by reference
            'variable': 'ref_replacement_6e4c1ae5ebbc48458fa8c5a00402ce11'
        }, {
            # Reference to parameter substituted
            'formula': 'ref_replacement_6e4c1ae5ebbc48458fa8c5a00402ce11',
            'id': 'd6896b62-c249-4cd8-915a-12c0682b2e52'
        }, {
            # Reference to PV substituted
            'formula': 'existing_pv_variable',
            'id': '57c91112-b260-4d14-bc95-0d2a0c4fc039'
        }, {
            # Reference to generated PV variable substituted
            'formula': 'ref_pv_replacement_5e4434c6bff345758c925eac120d7378',
            'id': '8c44da48-2d7a-4b39-b203-03544bfbd518'
        }]
    }]
    assert replace_implicit_references(input_ds) == expected
