# -*- coding: utf-8 -*-
from ..errors import UnresolvableActivityLink
from .utils import allocatable_production
from pprint import pformat
import logging


def check_activity_link_validity(data):
    """Check whether hard (activity) links can be resolved correctly.

    In order to make sure we get the correct exchange, hard links must be to either a reference product exchange or an allocatable byproduct. We can safely ignore other exchanges, e.g. losses, with the same product name if this condition is met.

    Raises ``UnresolvableActivityLink`` if an exchange can't be found."""
    mapping = {ds['id']: ds for ds in data}
    link_iterator = (exc
                     for ds in data
                     for exc in ds['exchanges']
                     if exc.get("activity link"))
    for link in link_iterator:
        ds = mapping[link['activity link']]
        found = [exc
                 for exc in allocatable_production(ds)
                 if exc['name'] == link['name']
                 and 'production volume' in exc]
        if len(found) == 1:
            continue
        elif len(found) > 1:
            message = "Found multiple candidates for activity link:\n{}\nTarget dataset:\n{}"
            raise UnresolvableActivityLink(message.format(pformat(link), ds['filepath']))
        else:
            message = "Found no candidates for activity link:\n{}\nTarget dataset:\n{}"
            raise UnresolvableActivityLink(message.format(pformat(link), ds['filepath']))
    return data
