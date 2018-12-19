# -*- coding: utf-8 -*-
from . import topology, RC_STRING
from ... import toolz
from ...data_helpers import production_volume
from ...errors import MissingSupplier
from ..utils import (
    get_single_reference_product,
    remove_exchange_uncertainty,
)
from ..uncertainty import scale_exchange
from .validation import no_overlaps, no_geo_duplicates
from copy import deepcopy
import logging

logger = logging.getLogger('ocelot')
detailed = logging.getLogger('ocelot-detailed')


def annotate_exchange(exc, ds):
    """Copy ``exc``, and add ``code``, ``technology level``, and ``location`` from dataset ``ds``.

    Also add dataset name as ``activity``."""
    FIELDS = ('location', 'code', 'technology level')
    exc = deepcopy(exc)
    exc.update({k: ds[k] for k in FIELDS if k in ds})
    exc['activity'] = ds['name']
    return exc

@no_geo_duplicates
def apportion_market_suppliers_to_consumers(consumers, suppliers):
    """Apportion suppliers to consumers based on their geographic relationships.

    Used only for reference products (other market inputs are linked by ``link_consumers_to_markets``).

    A supplier must be completely contained within a consumer. Region-specific markets (i.e. those without locations ``GLO`` or ``RoW``) do not consume from global providers.

    Modifies in place."""
    consumers_row = topology.resolve_row(
        [obj['location'] for obj in consumers
    ])

    for consumer in consumers:
        if 'suppliers' not in consumer:
            consumer['suppliers'] = []
        location = consumer['location']
        if location == 'RoW':
            location = consumers_row

        for name, group in toolz.groupby('name', suppliers).items():
            # Calculate separately for each technology (activity name)
            # No overlaps allowed per technology/product combo
            no_overlaps(group)

            suppliers_row = topology.resolve_row(
                [obj['location'] for obj in group
            ])
            sd = {o['location']: o for o in group}
            contained = [sd[key] for key in topology.contained(
                location, resolved_row=suppliers_row
            ).intersection(set(sd))]

            # ecoinvent doesn't work like this, unfortunately...
            # Could have saved myself a lot of trouble.

            # if not contained:
            #     # Nothing is inside or equal to this location.
            #     # Use an input which contains this location.
            #     contained = [ds for key, ds in sd.items()
            #                  if topology.contains(key, location, resolved_row=suppliers_row)]

            # if not contained:
            #     # Use RoW as backup (GLO would have already been used)
            #     # even if it doesn't actually cover this market
            #     contained = [ds for key, ds in sd.items() if key == 'RoW']
            #     logger.info({
            #         'type': 'table element',
            #         'data': (consumer['name'],
            #                  consumer['location'],
            #                  ";".join([o['location'] for o in group]), name)
            #     })
            consumer['suppliers'].extend([annotate_exchange(
                get_single_reference_product(obj),
                obj
            ) for obj in contained])

apportion_market_suppliers_to_consumers.__table__ = {
    'title': 'Defaulted to ``RoW`` suppliers, even though it fails GIS test.',
    'columns': ["Market name", "Market location", "Supplier locations", "Supplier name"]
}


def add_recycled_content_suppliers_to_markets(data):
    """Link markets to recycled content producing activities.

    At this point, the markets have not been modified in any way, but the recycled content cut-off processes have been created by ``create_recycled_content_datasets``. So, we have the following:

    * A market activity has a name ``market for foo``, and a reference product of ``foo``.
    * A new transforming activity has the name ``foo, Recycled Content cut-off``, and a reference product of ``foo, Recycled Content cut-off``.

    We need to correctly add the recycled content suppliers to these markets. The general purpose ``add_suppliers_to_markets`` doesn't work because the reference products are different."""
    market_filter = lambda x: x['type'] == "market activity"
    grouped = toolz.groupby("reference product", filter(market_filter, data))

    recycled_content_datasets = [
        x for x in data
        if x['type'] == 'transforming activity'
        and x['reference product'].endswith(RC_STRING)
    ]

    for rp, markets in grouped.items():
        suppliers = [
            ds for ds in recycled_content_datasets
            if ds['reference product'] == rp + RC_STRING
        ]
        no_overlaps(markets)
        if suppliers:
            apportion_market_suppliers_to_consumers(markets, suppliers)
    return data

add_recycled_content_suppliers_to_markets.__table__ = {
    'title': 'Allocate recycled content suppliers exchange amounts to markets',
    'columns': []
}


def add_suppliers_to_markets(data, from_type="transforming activity",
                             to_type="market activity"):
    """Add references to supplying exchanges to markets in field ``suppliers``.

    By default works with inputs to markets, but can be curried to work with market groups.

    Should only be run after ensuring that each dataset has one labeled reference product. Need to add actual exchange data because we need production volumes.

    Does not change the exchanges list or do allocation between various suppliers."""
    filter_func = lambda x: x['type'] in (from_type, to_type)
    grouped = toolz.groupby("reference product", filter(filter_func, data))

    for rp, datasets in grouped.items():
        suppliers = [ds for ds in datasets if ds['type'] == from_type]
        consumers = [ds for ds in datasets
                     if ds['type'] == to_type
                     # Could already have suppliers, e.g. recycled content cut-off
                     and not ds.get('suppliers')]
        if not consumers:
            continue
        if to_type == 'market activity':
            # Markets can't overlap
            no_overlaps(consumers)
        apportion_market_suppliers_to_consumers(consumers, suppliers)
    return data

add_suppliers_to_markets.__table__ = {
    'title': 'Add suppliers to region-specific markets',
    'columns': ["Name", "Product", "Market location", "Supplier locations"]
}


def allocate_all_market_suppliers(data, kind="market activity"):
    """Allocate all market activity suppliers.

    Uses the function ``allocate_suppliers``, which modifies data in place.

    """
    for ds in (o for o in data if o['type'] == kind):
        allocate_suppliers(ds)
    return data


def allocate_suppliers(dataset, is_market=True, exc=None):
    """Allocate suppliers to a market dataset and create input exchanges.

    The sum of the suppliers inputs should add up to the production amount of the market (reference product exchange amount), minus any constrained market links. Constrained market exchanges should already be in the list of dataset exchanges, with the attribute ``constrained``.

    ``is_market`` and ``exc`` options tested by ``link_consumers_to_markets`` tests."""
    if not exc:
        exc = get_single_reference_product(dataset)
    total_pv = sum(o['production volume']['amount']
                   for o in dataset['suppliers'])

    if not total_pv:
        if len(dataset['suppliers']) != 1:
            # TODO: Raise error here (or just allocate equally?)
            print("Skipping zero total PV with multiple inputs:\n\t{}/{} ({}, {} suppliers)".format(dataset['name'], exc['name'], dataset['location'], len(dataset['suppliers'])))
            return
        else:
            message = ("Assigning default production volume (single supplier, "
                       "zero PV): {} | {} | {}; supplier {} | {}")
            detailed.info({
                'ds': dataset,
                'message': message.format(
                    dataset['name'],
                    dataset['reference product'],
                    dataset['location'],
                    dataset['suppliers'][0]['name'],
                    dataset['suppliers'][0]['location'],
                ),
                'function': 'allocate_suppliers'
            })
            total_pv = dataset['suppliers'][0]['production volume']['amount'] = 4321
    else:
        message = "Production volume of {} {} divided into {} suppliers"
        detailed.info({
            'ds': dataset,
            'message': message.format(
                total_pv,
                exc['name'],
                len(dataset['suppliers']),
            ),
            'function': 'allocate_suppliers'
        })

    for supply_exc in dataset['suppliers']:
        scale_factor = supply_exc['production volume']['amount'] / total_pv
        if not scale_factor:
            continue
        if is_market:
            dataset['exchanges'].append(remove_exchange_uncertainty({
                'amount': scale_factor * exc['amount'],
                'name': supply_exc['name'],
                'unit': supply_exc['unit'],
                'type': 'from technosphere',
                'tag': 'intermediateExchange',
                'code': supply_exc['code']
            }))
        else:
            new_exc = scale_exchange(deepcopy(exc), scale_factor)
            new_exc.update({
                'type': 'from technosphere',
                'tag': 'intermediateExchange',
                'code': supply_exc['code'],
            })
            dataset['exchanges'].append(new_exc)

        message = "Create input exchange of {:.4g} {} for '{}' from '{}' ({})"
        detailed.info({
            'ds': dataset,
            'message': message.format(
                scale_factor * exc['amount'],
                supply_exc['unit'],
                exc['name'],
                supply_exc['name'],
                supply_exc['location']
            ),
            'function': 'allocate_suppliers'
        })

    if not is_market:
        dataset['exchanges'] = [x for x in dataset['exchanges'] if x != exc]

    return dataset


def update_market_production_volumes(data, kind="market activity"):
    """Update market production volumes to sum to the production volumes of all applicable inputs, minus any hard (activity) links to the market and to the market suppliers.

    By default works only on markets with type ``market activity``, but can be `curried <https://en.wikipedia.org/wiki/Currying>`__ to work on ``market group`` types as well.

    Activity link amounts are added by ``add_hard_linked_production_volumes`` and are currently given in ``rp_exchange['production volume']['subtracted activity link volume']``.

    Production volume is set to zero if the net production volume is negative."""
    def get_original_pv(exc):
        pv = exc['production volume']
        if 'original amount' in pv:
            return pv['original amount']
        else:
            return pv['amount']

    datasets = [o for o in data if o['type'] == kind]

    if kind == 'market group':
        # Need to sort in order of increasing size because
        # groups can be recursive.
        # RoW not allowed in market groups, so don't resolve
        flipped = lambda lst: ((y, x) for x, y in lst)
        ordered = dict(flipped(enumerate(topology.ordered_dependencies(datasets))))
        datasets.sort(
            key=lambda x: ordered[x['location']],
            reverse=True
        )

    for ds in datasets:
        rp = get_single_reference_product(ds)

        total_pv = sum(get_original_pv(o)
                       for o in ds['suppliers'])
        rp['production volume'][
        'original total']: total_pv
        missing_market_pv = rp['production volume'].get('subtracted activity link volume', 0)
        missing_inputs_pv = sum(
            s['production volume'].get("subtracted activity link volume", 0)
            for s in ds['suppliers']
        )
        pv = max(
            sum(s['production volume']['amount'] for s in ds['suppliers']) - missing_market_pv,
            0
        )
        rp['production volume']['amount'] = pv

        if kind == 'market group':
            # Update production volume of other references to this activity
            for other in datasets:
                if other == ds:
                    continue
                for supplier in other['suppliers']:
                    if supplier['code'] == ds['code']:
                        supplier['production volume'] = {'amount': pv}

        logger.info({
            'type': 'table element',
            'data': (ds['name'], rp['name'], ds['location'],
                     total_pv, missing_inputs_pv, missing_market_pv, pv)
        })
    return data

update_market_production_volumes.__table__ = {
    'title': 'Update market production volumes while subtracting hard links',
    'columns': ["Name", "Product", "Location", "Original", "Input subtractions", "Market subtractions", "Net"]
}


def delete_suppliers_list(data):
    """Delete the list of suppliers added by ``add_suppliers_to_markets``.

    This information was used by ``allocate_suppliers`` and ``update_market_production_volumes``, but is no longer useful."""
    for ds in data:
        if 'suppliers' in ds:
            del ds['suppliers']
    return data


def delete_whitelisted_zero_pv_market_datsets(data):
    """Remove some (but not all) global markets with zero production volume.

    Uses a white list of markets which are not in the ecoinvent 3.2 release."""
    can_delete_markets = {
        "market for heat, diffusion absorption heat pump",
        "market for heat, solar+electric, multiple-dwelling, for hot water",
        "market for heat, solar+gas, multiple-dwelling, for hot water",
        "market for heat, solar+gas, one-family house, for combined system",
        "market for heat, solar+gas, one-family house, for hot water",
        "market for heat, solar+wood, one-family house, for combined system",
        "market for nitro-compound",
        r"market for petrol, 85% ethanol by volume from biomass",
        "market for refinery gas",
        "market for spent oxychlor catalyst for ethylene dichloride production",
        "market for waste emulsion paint, on wall",
    }
    delete_me = lambda x: (x['type'] == 'market activity'
                           and x['name'] in can_delete_markets
                           and x['location'] == 'GLO')
    for ds in filter(delete_me, data):
        logger.info({
            'type': 'table element',
            'data': (ds['name'], ds['reference product'])
        })
    return [ds for ds in data if not delete_me(ds)]

delete_whitelisted_zero_pv_market_datsets.__table__ = {
    'title': 'Delete some global markets with zero production volume',
    'columns': ["Name", "Product"]
}


def assign_fake_pv_to_confidential_datasets(data):
    """Confidential datasets have production volumes of zero, because. Just because.

    In order to allocate these datasets to markets. In the absence of data, we assume all confidential datasets contribute equally."""
    confidential_names = {
        "anthraquinone production",
        "burnt shale production",
        "carboxymethyl cellulose production, powder",
        "citric acid production",
        "esters of versatic acid production",
        "feldspar production",
        "latex production",
        "layered sodium silicate production, SKS-6, powder",
        "particle board production, cement bonded",
        r"polycarboxylates production, 40% active substance",
        "sodium perborate production, monohydrate, powder",
        "sodium perborate production, tetrahydrate, powder",
        "sodium percarbonate production, powder",
        "wood wool boards production, cement bonded",
        "zeolite production, powder",
        r"zeolite production, slurry, without water, in 50% solution state",
    }
    confidential_filter = lambda x: (
        x['type'] == 'transforming activity'
        and x['name'] in confidential_names
    )
    for ds in filter(confidential_filter, data):
        rp = get_single_reference_product(ds)
        logger.info({
            'type': 'table element',
            'data': (ds['name'], rp['name'], 1)
        })
        rp['production volume']['amount'] = 1
    return data

assign_fake_pv_to_confidential_datasets.__table__ = {
    'title': 'Split inputs from confidential datasets equally because no production volume is available.',
    'columns': ["Name", "Product", "Production volume"]
}


def delete_global_markets_with_zero_pv_when_regional_market_present(data):
    """"""
    purge = []
    market_filter = lambda x: x['type'] == "market activity"
    grouped = toolz.groupby("reference product", filter(market_filter, data))
    for rp, group in grouped.items():
        if len(group) < 2:
            continue
        try:
            row = next(ds for ds in group if ds['location'] == 'RoW')
            assert not production_volume(row)
            purge.append(row)
            logger.info({
                'type': 'table element',
                'data': (row['name'], rp, row['location'])
            })
        except (StopIteration, AssertionError):
            continue
    return [ds for ds in data if ds not in purge]

delete_global_markets_with_zero_pv_when_regional_market_present.__table__ = {
    'title': 'Delete global markets with zero production volumes when regional markets are present',
    'columns': ["Name", "Product", "Location"]
}
