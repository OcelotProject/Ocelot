from . import test_data_dir
from ..io.extract_ecospold2 import generic_extractor
import os


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


def test_basic_extraction():
    fp = os.path.join(test_data_dir, "basic.xml")
    assert generic_extractor(fp) == BASIC_REFERENCE
