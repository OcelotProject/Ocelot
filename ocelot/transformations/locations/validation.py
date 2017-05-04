# -*- coding: utf-8 -*-
from ...errors import MultipleGlobalDatasets, OverlappingActivities
from . import topology
import wrapt


def check_single_global_dataset(datasets):
    """Raises ``MultipleGlobalDatasets`` if more than one global dataset is present."""
    if len([ds for ds in datasets if ds['location'] == 'GLO']) > 1:
        raise MultipleGlobalDatasets


def no_overlaps(data):
    """Check to make sure activities in ``data`` doesn't have geographic overlaps."""
    locations = [x['location'] for x in data]
    if topology.overlaps(locations):
        raise OverlappingActivities
    if 'GLO' in locations and len(locations) > 1:
        raise OverlappingActivities
    return True


@wrapt.decorator
def no_geo_duplicates(wrapped, instance, args, kwargs):
    """Check to make sure ``consumers`` doesn't have duplicate locations."""
    consumers = kwargs.get('consumers') or args[0]
    if len(consumers) != len({o['location'] for o in consumers}):
        raise ValueError("`consumers` has duplicate locations")
    return wrapped(*args, **kwargs)
