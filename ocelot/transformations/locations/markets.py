# -*- coding: utf-8 -*-
from . import topology
from ... import toolz
from ..utils import activity_grouper, get_single_reference_product
from .validation import no_overlaps, no_geo_duplicates
import logging


@no_overlaps
@no_geo_duplicates
def apportion_suppliers_to_consumers(consumers, suppliers):
    """Apportion suppliers to consumers based on their geographic relationships.

    Modifies in place."""
    spatial_dict = {
        consumer['location']: [supplier
                   for supplier in suppliers
                   if topology.contains(consumer['location'], supplier['location'])
        ]
        for consumer in consumers
        if consumer['location'] not in ("GLO", "RoW")
    }
    if spatial_dict:
        found_faces = set.union(*[topology(obj['location'])
                                  for supplier in spatial_dict.values()
                                  for obj in supplier])
    else:
        found_faces = set()

    # Add suppliers for GLO or RoW dataset
    row_consumers = [x for x in consumers if x['location'] in ("GLO", "RoW")]
    if row_consumers:
        spatial_dict[row_consumers.pop()['location']] = [
            supplier
            for supplier in suppliers
            if not topology(supplier['location']).intersection(found_faces)
        ]
        assert not row_consumers, "Multiple global market datasets found"

    # Validation checks
    if len(spatial_dict) != len(consumers):
        raise ValueError("Missing consumer datasets")
    if len(suppliers) != sum(len(o) for o in spatial_dict.values()):
        raise ValueError("Missing supplier datasets")
    if len(suppliers) != len({ds['location']
                              for lst in spatial_dict.values()
                              for ds in lst}):
        raise ValueError("Missing supplier locations")

    for ds in consumers:
        ds['suppliers'] = [get_single_reference_product(obj)
                           for obj in spatial_dict[ds['location']]]
        logging.info({
            'type': 'table element',
            'data': (ds['name'], ds['reference product'], ds['location'],
                     ";".join([o['location'] for o in spatial_dict[ds['location']]]))
        })


def add_suppliers_to_markets(data):
    """Add references to supplying exchanges to markets in field ``suppliers``.

    Should only be run after ensuring that each dataset has one labeled reference product. Need to add actual exchanges because we need production volumes.

    Does not change the exchanges list, nor do allocation between various suppliers."""
    filter_func = lambda x: x['type'] in ("transforming activity", "market activity")
    grouped = toolz.groupby("reference product", filter(filter_func, data))
    for datasets in grouped.values():
        suppliers = [ds for ds in datasets if ds['type'] == 'transforming activity']
        consumers = [ds for ds in datasets if ds['type'] == 'market activity']
        apportion_suppliers_to_consumers(consumers, suppliers)
    return data

add_suppliers_to_markets.__table__ = {
    'title': 'Add suppliers to region-specific markets',
    'columns': ["Name", "Product", "Market location", "Supplier locations"]
}


def allocate_suppliers(data):
    """Allocate suppliers to a market dataset.

    Works on both market activities and market groups.

    The sum of the suppliers inputs should add up to the production amount of the market (reference product exchange amount), minus any constrained market links. Constrained market exchanges should already be in the list of dataset exchanges, with the attribute ``constrained``."""
    pass

allocate_suppliers.__table__ = {
    'title': 'Allocate suppliers exchange amounts to markets',
    'columns': ["Name", "Product", "Market location", "Supplier locations"]
}


def link_consumers_to_markets(data):
    """Link exchange inputs to markets.

    Should only be run after ``add_suppliers_to_markets``.

    Add the field ``code`` to each exchange with the code of the linked activity."""
    pass
