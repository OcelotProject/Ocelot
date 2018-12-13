# -*- coding: utf-8 -*-
from . import topology
from ... import toolz
from ...data_helpers import production_volume
from ...errors import MarketGroupError
from ..uncertainty import scale_exchange
from ..utils import get_single_reference_product
from .markets import allocate_suppliers, annotate_exchange
import copy
import itertools
import logging
import numpy as np

logger = logging.getLogger('ocelot')
detailed = logging.getLogger('ocelot-detailed')


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

        # Note: The following works, and is tested, but we now raise an error
        # for market groups in `RoW`, as they are tricky to link to afterwards

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
        else:
            row_activities = []

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

        # Shouldn't exist - means that markets overlap
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


def check_markets_only_supply_one_market_group(data):
    """Validation function to make sure that a market only supplies one market group.

    Some markets have supplied multiple market groups in the past, probably due to a GIS implementation which considered one market group at a time.

    Raises a ``MarketGroupError`` if duplicate supply is found."""
    filter_func = lambda x: x['type'] == "market group"
    market_groups = dict(toolz.groupby(
        'name',
        filter(filter_func, data)
    ))

    code_dict = {x['code']: x for x in data}

    message = "Activity {} ({}) supplies multiple market groups: {} {} and {}."

    for name, groups in market_groups.items():
        for group in groups:
            input_codes = {exc['code'] for exc in group['exchanges']
                           if exc['type'] == 'from technosphere'}
            for other in (obj for obj in groups if obj is not group):
                for exc in (exc for exc in other['exchanges']
                            if exc['type'] == 'from technosphere'
                            and exc['code'] in input_codes):
                    # Duplicate are only prohibited if one market group is
                    # completely within another market group.
                    one = topology(group['location'])
                    two = topology(other['location'])
                    if one.difference(two) and two.difference(one):
                        continue

                    act = code_dict[exc['code']]
                    raise MarketGroupError(message.format(
                        act['name'], act['location'],
                        name, group['location'], other['location'],
                    ))
    return data


def check_no_row_market_groups(data):
    """Market groups are not allowed for ``RoW`` locations"""
    for ds in (o for o in data if o['type'] == "market group"):
        if ds['location'] == "RoW":
            raise MarketGroupError("Market groups can't be in `RoW`")
    return data


def get_next_biggest_candidate(location, candidates, subtract=None):
    if not candidates:
        return

    _ = lambda x: tuple(x) if x else None
    contained = topology.contained(location, subtract=_(subtract))
    possibles = sorted([
        (len(topology(candidate['location'])), candidate)
        for candidate in candidates
        if candidate['location'] in contained
    ], reverse=True)
    if possibles:
        return possibles[0][1]


def allocate_replacements(replacements):
    """Split ``amount`` among ``replacements`` by production volume.

    Also deletes key 'production volume' from exchanges."""
    total_pv = sum([o['production volume'] for o in replacements])
    if not total_pv:
        # Special case when missing production volumes.
        # Assume equal distribution
        total_pv = len(replacements)
        for obj in replacements:
            obj['production volume'] = 1

    for obj in replacements:
        scale_exchange(obj, obj['production volume'] / total_pv)
        del obj['production volume']

    return replacements


def link_market_group_consumers(data):
    """Link consumers to market groups, allocating by production volumes.
    Market groups must be contained by the consuming activity.

    This can't be done during market linking, because market groups haven't
    been linked to markets yet, and so have no production volumes.

    Assumes there is never a market group for ``RoW``.

    Market groups contained within a given activity location will by definition
    be only made up of markets also contained within the activity location."""
    market_groups = toolz.groupby(
        'reference product',
        (o for o in data if o['type'] == "market group")
    )

    codes = {o['code']: o for o in data}
    market_inputs = lambda ds: (exc for exc in ds['exchanges']
                                if exc['type'] == 'from technosphere'
                                and exc.get('code') and exc['amount']
                                and codes[exc['code']]['type'] == "market activity"
                                and 'activity link' not in exc)

    message = "Replaced market input {0} with market group: {1:.4f} fraction {2} to {3}"

    for ds in (o for o in data if o['type'] != "market group"):
        ds_replacements, purge = [], []
        for exc in market_inputs(ds):
            exc_replacements = []
            while True:
                mg = get_next_biggest_candidate(
                    ds['location'],
                    market_groups.get(exc['name']),
                    [o['location'] for o in exc_replacements]
                )
                if not mg:
                    break

                new_exc = annotate_exchange(exc, mg)
                new_exc['production volume'] = production_volume(mg, 0)
                exc_replacements.append(new_exc)

            if exc_replacements:
                purge.append(exc)
                allocate_replacements(exc_replacements)
                for obj in exc_replacements:
                    detailed.info({
                        'ds': ds,
                        'message': message.format(
                            obj['name'],
                            obj['amount'] / exc['amount'],
                            codes[exc['code']]['location'],
                            obj['location'],
                        ),
                        'function': 'link_market_group_consumers'
                    })
                ds_replacements.extend(exc_replacements)

        if ds_replacements:
            ds['exchanges'] = (
                [exc for exc in ds['exchanges'] if exc not in purge] +
                ds_replacements
            )
            logger.info({
                'type': 'table element',
                'data': (ds['name'], ds['reference product'], ds['location'])
            })

    return data

link_market_group_consumers.__table__ = {
    'title': "Substituted market group inputs",
    'columns': ["Name", "Flow", "Location"]
}


def no_row_market_groups(data):
    """Market groups can overlap, so there ``RoW`` is not allowed."""
    error_func = lambda ds: ds['type'] == "market group" and ds['location'] == 'RoW'
    if any(filter(error_func, data)):
        raise MarketGroupError("Market groups can't have location `RoW`")
    return data
