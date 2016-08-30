# -*- coding: utf-8 -*-
from ...errors import MultipleGlobalDatasets, OverlappingMarkets
from . import topology
from ... import toolz
import itertools


def check_single_global_dataset(datasets):
    """Raises ``MultipleGlobalDatasets`` if more than one global dataset is present."""
    if len([ds for ds in datasets if ds['location'] == 'GLO']) > 1:
        raise MultipleGlobalDatasets


def check_markets_dont_overlap(data):
    """Raise ``OverlappingMarkets`` if markets overlap."""
    markets = (ds for ds in data if ds['type'] == 'market activity')
    for rp, datasets in toolz.groupby('reference product', markets).items():
        faces = {ds['location']: topology(ds['location']) for ds in datasets}
        for first, second in itertools.combinations(faces, 2):
            if first in ("GLO", "RoW") or second in ("GLO", "RoW"):
                continue
            if faces[first].intersection(faces[second]):
                message = "Markets {} and {} for {} overlap"
                raise OverlappingMarkets(message.format(first, second, rp))
    return data
