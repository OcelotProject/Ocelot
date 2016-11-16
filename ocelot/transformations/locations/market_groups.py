# -*- coding: utf-8 -*-
from . import topology
from .markets import allocate_suppliers, annotate_exchange
from ..utils import get_single_reference_product
from ... import toolz
from ...errors import MarketGroupError
import itertools


def link_market_group_suppliers(data):
    """Link suppliers to market groups, and adjust production volumes."""
    filter_func = lambda x: x['type'] == "market group"
    market_groups = dict(toolz.groupby(
        'reference product',
        filter(filter_func, data)
    ))
    
    # Check to make sure names are consistent
    for group in market_groups.values():
        if not len({ds['name'] for ds in group}) == 1:
            raise MarketGroupError("Inconsistent activity names in market group")

    for ref_product, groups in market_groups.items():
        suppliers = [ds for ds in data 
                     if ds['type'] == 'market activity'
                     and ds['reference product'] == ref_product]

        location_lookup = {x['location']: x for x in suppliers}
        location_lookup.update({x['location']: x for x in groups})
        if not len(location_lookup) == len(suppliers) + len(groups):
            raise MarketGroupError("Market groups can't have same location as markets")

        tree = topology.tree(itertools.chain(suppliers, groups))

        # Turn `tree` from nested dictionaries to flat list of key, values.
        # Breadth first search
        def unroll(lst, dct):
            for key, value in dct.items():
                lst.append((key, value))
            for value in dct.values():
                if value:
                    lst = unroll(lst, value)
            return lst

        flat = unroll([], tree)

        for loc, children in flat:
            if children and not location_lookup[loc]['type'] == 'market group':
                raise MarketGroupError

        for parent, children in flat[::-1]:
            if not children:
                continue
            parent = location_lookup[parent]
            parent['suppliers'] = [annotate_exchange(
                    get_single_reference_product(location_lookup[obj]),
                    location_lookup[obj]
                ) for obj in children]
            allocate_suppliers(parent)

    return data
