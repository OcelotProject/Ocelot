# -*- coding: utf-8 -*-
from .. import toolz
from ..errors import MultipleGlobalDatasets
from .utils import activity_grouper
import logging


def check_single_global_dataset(datasets):
    """Raises ``MultipleGlobalDatasets`` if more than one global dataset is present."""
    if len([ds for ds in datasets if ds['location'] == 'GLO']) > 1:
        raise MultipleGlobalDatasets


def relabel_global_to_row(data):
    """Change ``GLO`` locations to ``RoW`` if there are region-specific datasets in the activity group."""
    processed = []
    for key, datasets in toolz.groupby(activity_grouper, data).items():
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
