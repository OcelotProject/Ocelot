# -*- coding: utf-8 -*-
from .. import toolz
from ..collection import Collection
from ..data_helpers import production_volume
from functools import partial
import logging
import pprint

logger = logging.getLogger('ocelot')


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


def mark_zero_pv_datasets(data, kind="transforming activity"):
    """Mark datasets with zero production volumes. Usually ``RoW`` datasets where
    all production occurs in regional datasets.

    Marks with ``ds['zero pv'] = True``."""
    activity_type_filter = lambda x: x['type'] == kind
    groups = toolz.groupby(
        'reference product',
        filter(activity_type_filter, data)
    ).items()
    for rp, group in groups:
        if len(group) == 1:
            continue
        zero_pv = [ds for ds in group if not production_volume(ds)]
        if len(zero_pv) == len(group):
            print("All {} datasets have no production volumes".format(rp))
        elif zero_pv:
            for ds in zero_pv:
                ds['zero pv'] = True
    return data


def purge_zero_pv_datasets(data):
    """Remove all datasets marked with zero production volumes"""
    for ds in data:
        if ds.get('zero pv'):
            logger.info({
                'type': 'table element',
                'data': (ds['name'], ds['reference product'], ds['location']),
            })
    return [ds for ds in data if not ds.get('zero pv')]

purge_zero_pv_datasets.__table__ = {
    'title': 'Remove activities with zero production volumes',
    'columns': ['Name', 'Flow', 'Location']
}


delete_all_zero_pv = Collection(
    "Remove activities with zero production volumes",
    mark_zero_pv_datasets,
    partial(mark_zero_pv_datasets, kind="market activity"),
    purge_zero_pv_datasets
)
