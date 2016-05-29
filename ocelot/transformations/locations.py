# -*- coding: utf-8 -*-
from .. import toolz
from ..utils import activity_grouper


def relabel_global_to_row(data, logger):
    """Change ``GLO`` locations to ``RoW`` if there are region-specific datasets in the activity group."""
    processed = []
    for key, datasets in toolz.groupby(activity_grouper, data).items():
        if len(datasets) > 1:
            for ds in datasets:
                if ds['location'] == 'GLO':
                    ds['location'] = 'RoW'
                    logger.log({
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
