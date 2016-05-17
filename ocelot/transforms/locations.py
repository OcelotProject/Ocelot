# -*- coding: utf-8 -*-
from .. import toolz
from ..utils import activity_grouper


def relabel_global_to_row(data, report):
    """Change ``GLO`` locations to ``RoW`` if there are region-specific datasets in the activity group."""
    processed = []
    for key, datasets in toolz.groupby(activity_grouper, data).items():
        if len(datasets) > 1:
            for ds in datasets:
                if ds['location'] == 'GLO':
                    ds['location'] = 'RoW'
                    report.log({
                        'type': 'table element',
                        'data': key
                    })
                processed.append(ds)
        else:
            processed.extend(datasets)
    return processed

relabel_global_to_row.__table__ = [
    ('changed_location', "Location converted to RoW")
]
