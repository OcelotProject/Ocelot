# -*- coding: utf-8 -*-
from .. import toolz
from ..errors import MultipleGlobalDatasets
from .utils import activity_grouper
import functools
import json
import logging
import os


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


class Topology(object):
    fp = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "..", "data", "faces.json"
    )

    compatibility = [
        ('IAI Area 1', "IAI Area 1, Africa"),
        ('IAI Area 3', "IAI Area 3, South America"),
        ("IAI Area 4&5 without China", 'IAI Area 4&5, without China'),
        ('IAI Area 8', "IAI Area 8, Gulf"),
    ]

    def __init__(self):
        self.data = {key: set(value) for key, value in
                     json.load(open(self.fp))['data']}
        for old, fixed in self.compatibility:
            self.data[old] = self.data[fixed]

    @functools.lru_cache(maxsize=512)
    def contained(self, location):
        if location == 'GLO':
            return
        faces = self.data[location]
        return {key
                for key, value in self.data.items()
                if key != location
                and not value.difference(faces)}

    @functools.lru_cache(maxsize=512)
    def intersects(self, location):
        if location == 'GLO':
            return
        faces = self.data[location]
        return {key
                for key, value in self.data.items()
                if key != location
                and value.intersection(faces)}
