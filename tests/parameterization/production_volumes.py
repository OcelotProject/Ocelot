# -*- coding: utf-8 -*-
from ocelot.io.validate_internal import dataset_schema
from ocelot.transformations.parameterization.production_volumes import create_pv_parameters


def test_create_pv_parameters_format():
    given = {
        "combined production": False,
        'access restricted': 'public',
        'economic scenario': '',
        'end date': '',
        'filepath': '',
        'id': '',
        'location': '',
        'start date': '',
        'type': 'transforming activity',
        'technology level': 'undefined',
        'name': 'test case',
        'exchanges': [{
            'amount': 42.,
            'id': '',
            'name': '',
            'tag': 'intermediateExchange',
            'type': 'from technosphere',
            'unit': 'kg',
            'production volume': {
                'variable': 'foo',
                'amount': 1.,
                'formula': 'bar ** 2'
            }
        }],
        'parameters': []
    }
    assert dataset_schema(create_pv_parameters(given)[0])

def test_create_pv_parameters_without_pv():
    given = {'exchanges': [{'foo': 'bar'}]}
    expected = [{'exchanges': [{'foo': 'bar'}]}]
    assert create_pv_parameters(given) == expected

def test_create_pv_parameters_create_parameter():
    given = {
        'name': 'test case',
        'exchanges': [{
            'unit': 'kg',
            'production volume': {
                'variable': 'foo',
                'amount': 1.,
                'formula': 'bar ** 2'
            }
        }],
        'parameters': []
    }
    expected = {
        'name': 'test case',
        'exchanges': [{
            'unit': 'kg',
            'production volume': {
                'amount': 1.,
            }
        }],
        'parameters': [{
            'unit': 'kg',
            'id': '',
            'name': 'Shifted PV parameter: foo',
            'variable': 'foo',
            'formula': 'bar ** 2',
            'amount': 1
        }]
    }
    result = create_pv_parameters(given)[0]
    result['parameters'][0]['id'] = ''
    assert result == expected

def test_create_pv_parameters_delete_formula():
    given = {
        'exchanges': [{
            'production volume': {
                'amount': 1.,
                'formula': 'bar ** 2'
            }
        }],
    }
    expected = {
        'exchanges': [{
            'production volume': {
                'amount': 1.,
            }
        }],
    }
    assert create_pv_parameters(given)[0] == expected
