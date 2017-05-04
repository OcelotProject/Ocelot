# -*- coding: utf-8 -*-
from ..data_helpers import production_volume
import pprint


def ensure_all_datasets_have_production_volume(data):
    """Make sure all datasets have a single reference product exchange with a valid production volume amount"""
    for ds in data:
        assert production_volume(ds), "Dataset does not have valid production volume:\n{}".format(pprint.pformat(ds))
    return data


def deparameterize(dataset):
    """Delete all variables and formulas from the dataset."""
    if 'parameters' in dataset:
        dataset['parameters'] = []
    for exc in dataset['exchanges']:
        for field in ('formula', 'variable'):
            if field in exc:
                del exc[field]
            if 'production volume' in exc:
                if field in exc['production volume']:
                    del exc['production volume'][field]
        if 'properties' in exc:
            del exc['properties']
    return dataset
