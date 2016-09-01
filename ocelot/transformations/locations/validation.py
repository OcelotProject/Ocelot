# -*- coding: utf-8 -*-
from ...errors import MultipleGlobalDatasets, OverlappingActivities
from . import topology
from ... import toolz
import itertools
import wrapt


def check_single_global_dataset(datasets):
    """Raises ``MultipleGlobalDatasets`` if more than one global dataset is present."""
    if len([ds for ds in datasets if ds['location'] == 'GLO']) > 1:
        raise MultipleGlobalDatasets


# def check_markets_dont_overlap(data):
#     """Raise ``OverlappingActivities`` if markets overlap."""
#     markets = (ds for ds in data if ds['type'] == 'market activity')
#     for rp, datasets in toolz.groupby('reference product', markets).items():
#         # Short circuit if don't need error message
#         if not topology.overlaps([ds['location'] for ds in datasets]):
#             continue

#         faces = {ds['location']: topology(ds['location']) for ds in datasets}
#         for first, second in itertools.combinations(faces, 2):
#             if first in ("GLO", "RoW") or second in ("GLO", "RoW"):
#                 continue
#             if faces[first].intersection(faces[second]):
#                 message = "Markets {} and {} for {} overlap"
#                 raise OverlappingActivities(message.format(first, second, rp))
#     return data


@wrapt.decorator
def no_overlaps(wrapped, instance, args, kwargs):
    """Check to make sure ``consumers`` doesn't have overlaps."""
    consumers = [x['location'] for x in (kwargs.get('consumers') or args[0])]
    if topology.overlaps(consumers):
        raise OverlappingActivities
    return wrapped(*args, **kwargs)


@wrapt.decorator
def no_geo_duplicates(wrapped, instance, args, kwargs):
    """Check to make sure ``consumers`` doesn't have duplicate locations."""
    consumers = kwargs.get('consumers') or args[0]
    if len(consumers) != len({o['location'] for o in consumers}):
        raise ValueError("`consumers` has duplicate locations")
    return wrapped(*args, **kwargs)
