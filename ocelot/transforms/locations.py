from . import toolz
from ..utils import extract_products_as_tuple


def relabel_global_to_row(data):
    grouper = lambda x: (x['name'], extract_products_as_tuple(x))
    processed = []
    for key, datasets in toolz.groupby(grouper, data).items():
        if len(datasets) > 1:
            for ds in datasets:
                if ds['location'] == 'GLO':
                    ds['location'] = 'RoW'
                processed.append(ds)
        else:
            processed.extend(datasets)
    return processed
