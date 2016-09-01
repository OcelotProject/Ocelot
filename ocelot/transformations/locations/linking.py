# -*- coding: utf-8 -*-
from ... import toolz
from ...errors import UnresolvableActivityLink
from ..utils import get_single_reference_product


def actualize_activity_links(data):
    """Add ``code`` field to activity links."""
    mapping = toolz.groupby("id", data)
    link_iterator = (exc
                     for ds in data
                     for exc in ds['exchanges']
                     if exc.get("activity link"))
    for link in link_iterator:
        references = [ds
                      for ds in mapping[link['activity link']]
                      if ds['reference product'] == link['name']]
        if len(references) != 1:
            message = "Can't resolve activity link: {}"
            raise UnresolvableActivityLink(message.format(link['activity link']))
        link['code'] = references[0]['code']
    return data
