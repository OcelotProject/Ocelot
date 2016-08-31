# -*- coding: utf-8 -*-
from . import topology
from ... import toolz
from ..utils import activity_grouper, get_single_reference_product
import logging


def apportion_suppliers_to_consumers(datasets, from_type, to_type):
    """Apportion ``datasets`` suppliers with type ``from_type`` to consumers with type ``to_type``.

    Modifies in place."""
    # Note: This won't populate for GLO/RoW
    spatial_dict = {
        ds: [o
             for o in datasets
             if o['type'] == from_type
             and topology.contains(ds['location'], o['location'])
        ]
        for ds in datasets
        if ds['type'] == to_type
    }

    # Check that existing suppliers don't overlap
    # Shouldn't be possible because we check that markets don't overlap
    all_linked_locations = {
        o['location']
        for lst in spatial_dict.values()
        for o in lst
    }
    all_linked_total = sum([len(o) for o in spatial_dict.values()])
    if len(all_linked_locations) != all_linked_total:
        raise ValueError("Overlapping suppliers found")

    # Add suppliers to GLO/RoW
    if "GLO" in spatial_dict or "RoW" in spatial_dict:
        pass

    all_suppliers_total = len(1 for ds in datasets if ds['type'] == from_type)

    if all_suppliers_total != all_linked_total:
        raise ValueError("Some dataset weren't linked to region-specific markets, and no GLO/RoW present")
    for k, v in spatial_dict.items():
        k['suppliers'] = [get_single_reference_product(o) for o in v]


def add_suppliers_to_markets(data, from_type="transforming activity", to_type="market activity"):
    """Add references to supplying exchanges to markets in field ``suppliers``.

    Should only be run after ensuring that each dataset has one labeled reference product.

    Need to add actual exchanges because we need production volumes.

    By default links transforming activities to market activities, but can also support market groups with the parameters ``from_type`` and ``to_type``.

    Does not change the exchanges list, nor do allocation between various suppliers."""
    filter_func = lambda x: x['type'] in (from_type, to_type)
    grouped = toolz.groupby("reference product", filter(filter_func, data))
    for datasets in grouped.values():
        apportion_suppliers_to_consumers(datasets)
    return data

add_suppliers_to_markets.__table__ = {
    'title': 'Activities changed from `GLO` to `RoW`',
    'columns': ["Name", "Product(s)"]
}


def allocate_suppliers(data):
    """Allocate suppliers to a market dataset.

    Works on both market activities and market groups.

    The sum of the suppliers inputs should add up to the production amount of the market (reference product exchange amount), minus any constrained market links. Constrained market exchanges should already be in the list of dataset exchanges, with the attribute ``constrained``."""
    pass


def link_consumers_to_markets(data):
    """Link exchange inputs to markets.

    Should only be run after ``add_suppliers_to_markets``.

    Add the field ``code`` to each exchange with the code of the linked activity."""
    pass
