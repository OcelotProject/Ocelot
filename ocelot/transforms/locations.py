from . import toolz
from ..utils import activity_grouper


def relabel_global_to_row(data):
    processed = []
    for key, datasets in toolz.groupby(activity_grouper, data).items():
        if len(datasets) > 1:
            for ds in datasets:
                if ds['location'] == 'GLO':
                    ds['location'] = 'RoW'
                processed.append(ds)
        else:
            processed.extend(datasets)
    return processed
