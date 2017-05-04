# -*- coding: utf-8 -*-
from ... import toolz
from ...collection import Collection
import logging


def log_conflicting_technology_levels(data):
    """Log anytime that there are both ``undefined`` and ``current`` inputs to a market.

    The behaviour when this condition occurs is undefined. We will later change all technology levels with ``undefined`` to ``current``, but there is no general rule what to prefer if there are already ``current`` activities in the market mix."""
    activity_ds_filter = lambda x: x['type'] == 'transforming activity'
    has_undefined = lambda x: any(ds for ds in x if ds['technology level'] == 'undefined')
    has_current = lambda x: any(ds for ds in x if ds['technology level'] == 'current')
    for rp, datasets in toolz.groupby('reference product',
                                      filter(activity_ds_filter, data)).items():
        if has_undefined(datasets) and has_current(datasets):
            logging.info({
                'type': 'table element',
                'data': (rp, len(datasets))
            })
    return data

log_conflicting_technology_levels.__table__ = {
    'title': 'Log when both ``undefined`` and ``current`` are present in a market mix',
    'columns': ["Reference product", "Number of datasets"]
}


def switch_undefined_to_current(data):
    activity_ds_filter = lambda x: x['type'] == 'transforming activity'
    for ds in filter(activity_ds_filter, data):
        if ds['technology level'] == 'undefined':
            ds['technology level'] = 'current'
            logging.info({
                'type': 'table element',
                'data': (ds['name'], ds['reference product'], ds['location'])
            })
    return data

switch_undefined_to_current.__table__ = {
    'title': 'Switch all `undefined` activity technology levels to `current`',
    'columns': ["Reference product", "Number of datasets"]
}


cleanup_technology_levels = Collection(
    log_conflicting_technology_levels,
    switch_undefined_to_current,
)
