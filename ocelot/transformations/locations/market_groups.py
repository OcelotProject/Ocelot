# -*- coding: utf-8 -*-
from . import topology
from ... import toolz
from ...errors import MarketGroupError
from ..utils import get_single_reference_product
from .markets import allocate_suppliers, annotate_exchange
import copy
import itertools
import logging

logger = logging.getLogger('ocelot')


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

        # Put groups second so that if there are duplicates, the group will be retrieved
        location_lookup = {x['location']: x for x in suppliers}
        supplier_lookup = copy.deepcopy(location_lookup)
        location_lookup.update({x['location']: x for x in groups})

        tree = topology.tree(itertools.chain(suppliers, groups))

        if [1 for x in groups if x['location'] == 'RoW']:
            # Handling RoW is a little tricky. The RoW market group can contain
            # markets which are not covered by other market groups. So we have
            # to resolve what RoW means in each context.
            row_faces = topology('__all__').difference(
                set.union(*[topology(x['location']) for x in groups])
            )
            # This will include RoW, if present, but not GLO
            row_activities = [x for x in suppliers
                              if not topology(x['location']).difference(row_faces)
                              and x['location'] != 'GLO']

            # RoW suppliers need to be removed from GLO suppliers
            if 'GLO' in tree:
                for obj in row_activities:
                    if (obj['location'] != 'RoW'
                        and obj['location'] in tree['GLO']):
                        del tree['GLO'][obj['location']]

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

        def translate(obj):
            return annotate_exchange(get_single_reference_product(obj), obj)

        for parent, children in flat[::-1]:
            # Special case RoW
            if parent == 'RoW':
                obj = location_lookup[parent]
                obj['suppliers'] = [translate(act) for act in row_activities]
            else:
                obj = location_lookup[parent]
                obj['suppliers'] = [translate(location_lookup[child])
                                    for child in children]

            # Also add supplier if market and market group have same location
            if (parent in supplier_lookup
                and location_lookup[parent]['type'] == 'market group'
                and parent != 'RoW'):
                obj['suppliers'].append(translate(supplier_lookup[parent]))

            # For consistency in testing
            obj['suppliers'].sort(key=lambda x: x['code'])

            for exc in obj['suppliers']:
                logger.info({
                    'type': 'table element',
                    'data': (obj['name'], obj['location'], exc['location'])
                })

            if not obj['suppliers']:
                del obj['suppliers']
                continue

            allocate_suppliers(obj)

    return data

link_market_group_suppliers.__table__ = {
    'title': "Link and allocate suppliers for market groups. Suppliers can be market activities or other market groups.",
    'columns': ["Name", "Location", "Supplier Location"]
}
