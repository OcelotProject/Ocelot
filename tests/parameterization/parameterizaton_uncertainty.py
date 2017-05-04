# -*- coding: utf-8 -*-
from ocelot.transformations.parameterization.uncertainty import repair_all_uncertainty_distributions as repair
import numpy as np


def test_repair():
    given = [{
        'exchanges': [{
            'amount': -4,
            'uncertainty': {
                'type': 'lognormal',
                'variance with pedigree uncertainty': 0.7
            },
            'pedigree matrix': {}
        }, {
            'amount': 0,
            'uncertainty': {'type': 'lognormal'}
        }]
    }]
    expected = [{
        'exchanges': [{
            'amount': -4,
            'pedigree matrix': {},
            'uncertainty': {
                'type': 'lognormal',
                'mean': 4,
                'mu': np.log(4),
                'negative': True,
                'variance': 0.7,
                'variance with pedigree uncertainty': 0.7
            },
        }, {
            'amount': 0
        }]
    }]
    assert repair(given) == expected
