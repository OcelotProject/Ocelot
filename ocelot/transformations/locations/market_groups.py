# -*- coding: utf-8 -*-
from . import topology
from ... import toolz
from ...data_helpers import production_volume
from ...errors import MarketGroupError
from ..uncertainty import scale_exchange
from ..utils import get_single_reference_product
from .markets import (
    allocate_suppliers,
    annotate_exchange,
    update_market_production_volumes,
)
import copy
import itertools
import logging
import numpy as np

logger = logging.getLogger('ocelot')
detailed = logging.getLogger('ocelot-detailed')


def link_market_group_suppliers(data):
    """Link suppliers to market groups and populate ``dataset['suppliers']``.

    Market groups can overlap, so our strategy is to fill up the market groups starting with the largest suppliers contained within the location. We choose between markets and market groups simultaneously, preferring markets over market groups if they have the same location (which is normally not allowed). Sorting is done using ``topology.default_size_proxy``, which currently counts the number of topological faces.

    The same market can supply more than one market group, such as individual country mixes supplying the market groups for ENTSO-E and Europe without Switzerland.

    Market group locations can never be ``RoW``, as market groups overlap.
    """
    filter_func = lambda x: x['type'] == "market group"
    market_groups = dict(toolz.groupby(
        'reference product',
        filter(filter_func, data)
    ))

    # Check to make sure names are consistent
    for group in market_groups.values():
        if not len({ds['name'] for ds in group}) == 1:
            raise MarketGroupError("Inconsistent activity names in market group")

    for ref_product, group in market_groups.items():
        markets = {ds['location']: ds for ds in data
                     if ds['type'] == 'market activity'
                     and ds['reference product'] == ref_product}
        mg_by_location = {ds['location']: ds for ds in group}

        if 'RoW' in markets:
            resolved_supplier_row = topology.resolve_row(markets)
        else:
            resolved_supplier_row = set()

        together = set(markets).union(set(mg_by_location))
        ordered = topology.ordered_dependencies(
            [{'location': l} for l in together],
            resolved_supplier_row
        )

        for loc in mg_by_location:
            ds = mg_by_location[loc]
            found, to_add = [], []

            for candidate in ordered:
                if topology.contains(loc, candidate, subtract=found, resolved_row=resolved_supplier_row):
                    if candidate in markets:
                        found.append(candidate)
                        to_add.append(markets[candidate])
                    elif candidate != loc:
                        # Skip our own output
                        found.append(candidate)
                        to_add.append(mg_by_location[candidate])

            ds['suppliers'] = [
                annotate_exchange(
                    get_single_reference_product(obj),
                    obj
                ) for obj in sorted(
                    to_add,
                    key=lambda x: x['code']
                )
            ]

            if not ds['suppliers']:
                del ds['suppliers']
                continue

            for exc in ds['suppliers']:
                logger.info({
                    'type': 'table element',
                    'data': (ds['name'], ds['location'], exc['location'])
                })
    return data

link_market_group_suppliers.__table__ = {
    'title': "Link and allocate suppliers for market groups. Suppliers can be market activities or other market groups.",
    'columns': ["Name", "Location", "Supplier Location"]
}


def check_no_row_market_groups(data):
    """Market groups are not allowed for ``RoW`` locations"""
    for ds in (o for o in data if o['type'] == "market group"):
        if ds['location'] == "RoW":
            raise MarketGroupError("Market groups can't be in `RoW`")
    return data
