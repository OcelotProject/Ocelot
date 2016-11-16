# -*- coding: utf-8 -*-
from . import topology
from .markets import allocate_suppliers, annotate_exchange


"""
consumer['suppliers'] = [annotate_exchange(
    get_single_reference_product(obj),
    obj
) for obj in contained]
"""


def link_market_group_suppliers(data):
    """Link suppliers to market groups, and adjust production volumes."""



    """Link technosphere exchange inputs to markets.

    Should only be run after ``add_suppliers_to_markets``. Skips hard (activity) links, and exchanges which have already been linked.

    Add the field ``code`` to each exchange with the code of the linked market activity."""
    filter_func = lambda x: x['type'] == "market activity"
    market_mapping = toolz.groupby(
        'reference product',
        filter(filter_func, data)
    )
    for ds in data:
        for exc in filter(unlinked, ds['exchanges']):
            try:
                contained = [
                    market
                    for market in market_mapping[exc['name']]
                    if topology.contains(market['location'], ds['location'])]
                assert contained
            except (KeyError, AssertionError):
                continue
            if len(contained) == 1:
                sup = contained[0]
                exc['code'] = sup['code']

                message = "Link input of '{}' to '{}' ({})"
                detailed.info({
                    'ds': ds,
                    'message': message.format(exc['name'], sup['name'], sup['location']),
                    'function': 'link_consumers_to_regional_markets'
                })
            else:
                # Shouldn't be possible - markets shouldn't overlap
                message = "Multiple markets contain {} in {}:\n{}"
                raise OverlappingMarkets(message.format(
                    exc['name'],
                    ds['location'],
                    [x['location'] for x in contained])
                )
    return data