# -*- coding: utf-8 -*-
from . import test_data_dir
from ocelot.io.extract_ecospold2 import generic_extractor
import os

# Tests for ecospold2 extraction


BASIC_REFERENCE = [{
    'economic': 'Business-as-Usual',
    'exchanges': [{
        'amount': -0.99,
        'id': '3b954491-a88c-484d-8332-d3941828cb4c',
        'name': 'Dr. Brayden Kilback IV',
        'production volume': {'amount': 0.0029892},
        'tag': 'intermediateExchange',
        'type': 'from technosphere',
        'uncertainty': {
            'mean': 1.,
            'mu': 2.,
            'pedigree matrix': (1, 2, 3, 4, 5),
            'type': 'lognormal',
            'variance': 3.,
            'varianceWithPedigreeUncertainty': 4.
        },
        'unit': 'm3'
    }, {
        'amount': 0.1,
        'compartments': ('air', 'unspecified'),
        'id': 'fd251456-233f-4425-aba8-38ca43bf8095',
        'name': 'Water',
        'tag': 'elementaryExchange',
        'type': 'to environment',
        'uncertainty': {
            'mean': 1.,
            'mu': 2.,
            'pedigree matrix': (1, 2, 3, 4, 5),
            'type': 'lognormal',
            'variance': 3.,
            'varianceWithPedigreeUncertainty': 4.
        },
        'unit': 'm3'
    }],
    'location': 'RoW',
    'name': 'Miss Morgan Wolf',
    'technology level': 'current',
    'temporal': ('1996-01-01', '2015-12-31'),
    'type': 'transforming activity'
}]

PROD_VOLUME_REFERENCE = [{
    'economic': 'Business-as-Usual',
    'exchanges': [{
        'amount': 1.0,
        'id': 'fb31ee9b-d01e-4121-9732-01b9bdd491ef',
        'name': 'Messiah Schiller',
        'production volume': {
            'amount': 23.0,
            'uncertainty': {
                'mean': 1.0,
                'mu': 2.0,
                'pedigree matrix': (1, 2, 3, 4, 5),
                'type': 'lognormal',
                'variance': 3.0,
                'varianceWithPedigreeUncertainty': 4.0
            },
            'variable': 'Cason_Volkman'
        },
        'tag': 'intermediateExchange',
        'type': 'reference product',
        'unit': 'kWh',
    }, {
        'amount': -1.8,
        'id': 'e1c9f077-547d-4c10-81c1-148e4a7e0df0',
        'name': 'Ellery Crooks',
        'production volume': {
            'amount': 4.0,
            'formula': 'fly_ash * apv_electricity'
        },
        'tag': 'intermediateExchange',
        'type': 'from technosphere',
        'uncertainty': {
            'mean': 1.0,
            'mu': 2.0,
            'pedigree matrix': (1, 2, 3, 4, 5),
            'type': 'lognormal',
            'variance': 3.0,
            'varianceWithPedigreeUncertainty': 4.0
        },
        'unit': 'kg',
        'variable': 'fly_ash',
    }],
    'location': 'TW',
    'name': 'Jagger Lakin',
    'technology level': 'modern',
    'temporal': ('1990-01-01', '2015-12-31'),
    'type': 'transforming activity'
}]

MULTIOUTPUT_REFERENCE = [{
    'combined production': True,
    'economic': 'Business-as-Usual',
    'exchanges': [{'amount': 200.0,
        'formula': 'carmel_reynolds + 32',
        'id': 'eae837b7-7775-4b3a-a5cd-c4c38b63dbea',
        'name': 'Dr. Jeana Considine MD',
        'production volume': {'amount': 318.0},
        'properties': [{
            'amount': 168.0,
            'id': '0ae5715b-3b9d-455e-a757-107c3ed8d6a3',
            'name': 'price',
            'variable': 'carmel_reynolds'
        }, {
            'amount': 0.6,
            'formula': 'miss_bette_kirlin',
            'id': 'a9358458-9724-4f03-b622-106eda248916',
            'name': 'water content',
            'uncertainty': {
                'mean': 1.0,
                'mu': 2.0,
                'pedigree matrix': (1, 2, 3, 4, 5),
                'type': 'lognormal',
                'variance': 3.0,
                'varianceWithPedigreeUncertainty': 4.0
            }
        }],
        'tag': 'intermediateExchange',
        'type': 'reference product',
        'unit': 'm3',
        'variable': 'pulpwood'
    }, {
        'amount': 34.0,
        'formula': 'raiden_thompson',
        'id': '667e76dc-d54f-4062-a75c-01932128f788',
        'name': 'Mr. Perley Hessel II',
        'production volume': {
            'amount': 19.0,
            'uncertainty': {
                'mean': 19.0,
                  'mu': 2.0,
                  'pedigree matrix': (1, 2, 3, 4, 5),
                  'type': 'lognormal',
                  'variance': 3.0,
                  'varianceWithPedigreeUncertainty': 4.0
            }
        },
        'tag': 'intermediateExchange',
        'type': 'reference product',
        'unit': 'kg',
        'variable': 'greenholt'}
    ],
    'location': 'GLO',
    'name': 'Aliana Price',
    'parameters': [{
        'formula': 'alia_botsford * 42',
        'name': 'Raiden Thompson IV',
        'variable': 'raiden_thompson'
    }, {
        'name': 'Mrs. Alia Botsford',
        'uncertainty': {
            'mean': 1.0,
            'mu': 2.0,
            'pedigree matrix': (1, 2, 3, 4, 5),
            'type': 'lognormal',
            'variance': 3.0,
            'varianceWithPedigreeUncertainty': 4.0
        },
        'variable': ' alia_botsford'
    }],
    'technology level': 'current',
    'temporal': ('2010-01-01', '2015-12-31'),
    'type': 'transforming activity'
}]


def test_basic_extraction():
    fp = os.path.join(test_data_dir, "basic.xml")
    BASIC_REFERENCE[0]['filepath'] = fp
    assert generic_extractor(fp) == BASIC_REFERENCE


def test_production_volume_extraction():
    fp = os.path.join(test_data_dir, "prod_volume.xml")
    PROD_VOLUME_REFERENCE[0]['filepath'] = fp
    assert generic_extractor(fp) == PROD_VOLUME_REFERENCE


def test_multioutput_extraction():
    fp = os.path.join(test_data_dir, "parameterized_multioutput.xml")
    MULTIOUTPUT_REFERENCE[0]['filepath'] = fp
    assert generic_extractor(fp) == MULTIOUTPUT_REFERENCE
