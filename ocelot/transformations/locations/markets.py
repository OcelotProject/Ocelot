# -*- coding: utf-8 -*-
from ... import toolz
from ..utils import activity_grouper
from . import topology
import logging


def add_suppliers_to_markets(data):
    """Add ."""
    processed = []
    # for key, datasets in toolz.groupby(activity_grouper, data).items():
        if len(datasets) > 1:
            check_single_global_dataset(datasets)
            for ds in datasets:
                if ds['location'] == 'GLO':
                    ds['location'] = 'RoW'
                    logging.info({
                        'type': 'table element',
                        'data': (key[0], "; ".join(sorted(key[1])))
                    })
                processed.append(ds)
        else:
            processed.extend(datasets)
    return processed

relabel_global_to_row.__table__ = {
    'title': 'Activities changed from `GLO` to `RoW`',
    'columns': ["Name", "Product(s)"]
}
