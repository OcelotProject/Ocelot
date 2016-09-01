# -*- coding: utf-8 -*-
from . import topology
from ... import toolz
from ..utils import (
    activity_grouper,
    get_single_reference_product,
    remove_exchange_uncertainty,
)
from .validation import no_overlaps, no_geo_duplicates
from copy import deepcopy
import logging


def annotate_exchange(exc, ds):
    """Copy ``exc``, and add ``code`` and ``location`` from ``ds``."""
    exc = deepcopy(exc)
    exc.update({k: ds[k] for k in ('location', 'code')})
    return exc


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

    for ds in consumers:
        ds['suppliers'] = [annotate_exchange(get_single_reference_product(obj),
                                             obj)
                           for obj in spatial_dict[ds['location']]]
        logging.info({
            'type': 'table element',
            'data': (ds['name'], ds['reference product'], ds['location'],
                     ";".join([o['location'] for o in spatial_dict[ds['location']]]))
        })


def add_suppliers_to_markets(data, from_type="transforming activity",
                             to_type="market activity"):
    """Add references to supplying exchanges to markets in field ``suppliers``.

    By default works with inputs to markets, but can be curried to work with market groups.

    Should only be run after ensuring that each dataset has one labeled reference product. Need to add actual exchange data because we need production volumes.

    Does not change the exchanges list or do allocation between various suppliers."""
    filter_func = lambda x: x['type'] in (from_type, to_type)
    grouped = toolz.groupby("reference product", filter(filter_func, data))
    for datasets in grouped.values():
        suppliers = [ds for ds in datasets if ds['type'] == from_type]
        consumers = [ds for ds in datasets if ds['type'] == to_type]
        apportion_suppliers_to_consumers(consumers, suppliers)
    return data

add_suppliers_to_markets.__table__ = {
    'title': 'Add suppliers to region-specific markets',
    'columns': ["Name", "Product", "Market location", "Supplier locations"]
}


def allocate_suppliers(data):
    """Allocate suppliers to a market dataset and create input exchanges.

    Works on both market activities and market groups.

    The sum of the suppliers inputs should add up to the production amount of the market (reference product exchange amount), minus any constrained market links. Constrained market exchanges should already be in the list of dataset exchanges, with the attribute ``constrained``."""
    MARKETS = ("market activity", "market group")
    for ds in (o for o in data if o['type'] in MARKETS):
        rp = get_single_reference_product(ds)
        scale_factor = rp['amount']
        total_pv = sum(o['production volume']['amount']
                       for o in ds['suppliers'])
        for supply_exc in ds['suppliers']:
            amount = supply_exc['production volume']['amount'] / total_pv * scale_factor
            ds['exchanges'].append(remove_exchange_uncertainty({
                'amount': amount,
                'name': supply_exc['name'],
                'unit': supply_exc['unit'],
                'type': 'from technosphere',
                'tag': 'intermediateExchange',
                'code': supply_exc['code']
            }))
            logging.info({
                'type': 'table element',
                'data': (ds['name'], rp['name'], ds['location'],
                         supply_exc['location'], amount)
            })
    return data

allocate_suppliers.__table__ = {
    'title': 'Allocate suppliers exchange amounts to markets',
    'columns': ["Name", "Product", "Location", "Supplier location", "Amount"]
}


def update_market_production_volumes(data, kind="market activity"):
    """Update market production volumes to sum to the production volumes of all applicable inputs, minus any hard (activity) links.

    By default works only on market activities, but can be curried to work on market groups.

    Activity link amounts are added by ``add_hard_linked_production_volumes`` and are given in the field ``rp_exchange['production volume']['subtracted activity link volume']``.

    Production volume is set to zero is the net production volume is negative."""
    for ds in (o for o in data if o['type'] == kind):
        rp = get_single_reference_product(ds)
        total_pv = sum(o['production volume']['amount']
                       for o in ds['suppliers'])
        try:
            missing_pv = rp['production volume'].pop('subtracted activity link volume')
        except KeyError:
            missing_pv = 0
        rp['production volume']['amount'] = max(total_pv - missing_pv, 0)
        logging.info({
            'type': 'table element',
            'data': (ds['name'], rp['name'], total_pv, missing_pv, rp['production volume']['amount'])
        })
    return data

update_market_production_volumes.__table__ = {
    'title': 'Update market production volumes while subtracting hard links',
    'columns': ["Name", "Product", "Total", "Activity links", "Net"]
}


def delete_suppliers_list(data):
    """Delete the list of suppliers added by ``add_suppliers_to_markets``.

    This information was used by ``allocate_suppliers`` and ``update_market_production_volumes``, but is no longer useful."""
    for ds in data:
        if 'suppliers' in ds:
            del ds['suppliers']
    return data


def link_consumers_to_markets(data):
    """Link technosphere exchange inputs to markets.

    Should only be run after ``add_suppliers_to_markets``. Skips hard (activity) links, and exchanges which have already been linked.

    Add the field ``code`` to each exchange with the code of the linked market activity."""
    filter_func = lambda x: x['type'] == "market activity"
    # Cache markets by reference product so don't need to iterate through whole list each time
    market_mapping = toolz.groupby(
        'reference product',
        filter(filter_func, data)
    )
    for ds in data:
        for exc in ds['exchanges']:
            if (exc.get('code') or exc.get('activity link')
                or not exc['type'] == 'from technosphere'):
                continue
            contributors = [m for m in market_mapping[exc['name']]
                            if topology.contains(m['location'], ds['location'])]
            if len(contributors) == 1:
                exc['code'] = contributors[0]['code']
            else:
                print("Need to split exchanges")
                # total_pv = sum(get_single_reference_product(m)['production volume']['amount']
                #                for m in contributors)
    return data
