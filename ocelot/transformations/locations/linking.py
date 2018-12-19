# -*- coding: utf-8 -*-
from . import topology, RC_STRING
from ... import toolz
from ...data_helpers import production_volume
from ...errors import OverlappingMarkets, MissingSupplier
from ..utils import get_single_reference_product
from .markets import allocate_suppliers, annotate_exchange
import logging


logger = logging.getLogger('ocelot')
detailed = logging.getLogger('ocelot-detailed')

unlinked = lambda x: x['type'] == 'from technosphere' and not x.get('code')


def actualize_activity_links(data):
    """Add ``code`` field to activity links."""
    mapping = toolz.groupby("id", data)
    link_iterator = ((exc, ds)
                     for ds in data
                     for exc in ds['exchanges']
                     if exc.get("activity link"))
    for link, ds in link_iterator:
        references = [ds
                      for ds in mapping[link['activity link']]
                      if ds['reference product'] == link['name']]
        if len(references) != 1:
            # TODO: Resolve all sorts of special cases...
            # Just logging for now
            logger.info({
                'type': 'table element',
                'data': (link['activity link'], link['name'], link['amount'])
            })
            continue
            # raise UnresolvableActivityLink(message.format(link['activity link']))
        message = "Linked input of '{}' to activity '{}' ({})."
        found = references[0]
        detailed.info({
            'ds': ds,
            'function': 'actualize_activity_links',
            'message': message.format(link['name'], found['name'], found['location'])
        })
        link['code'] = found['code']
    return data

actualize_activity_links.__table__ = {
    'title': "Turn activity links into references to activity codes. This table lists references that couldn't be resolved.",
    'columns': ["Activity link", "Name", "Amount"]
}


def link_consumers_to_recycled_content_activities(data):
    """Link technosphere exchange inputs to activities that produce ``Recycled Content`` products.

    Only for inputs of recyclable byproducts in cutoff system model. In these dataset, linking doesn't go through a market, but goes directly to the transforming activity.

    Add the field ``code`` to each exchange with the code of the linked market activity."""
    recycled_content_filter = lambda x: (
        RC_STRING in x['reference product']
        and x['type'] == 'transforming activity')
    recycled_content_mapping = toolz.groupby(
        'reference product',
        filter(recycled_content_filter, data)
    )

    for ds in data:
        for exc in filter(unlinked, ds['exchanges']):
            try:
                contributors = recycled_content_mapping[exc['name']]
                # Recycled Content producers are all global
                assert len(contributors) == 1
            except (KeyError, AssertionError):
                continue

            sup = contributors[0]
            exc['code'] = sup['code']
            logger.info({
                'type': 'table element',
                'data': (ds['name'], exc['name'], ds['location'], sup['name'])
            })
    return data

link_consumers_to_recycled_content_activities.__table__ = {
    'title': 'Link input exchanges to cutoff recycled content producers',
    'columns': ["Consumer name", "Product", "Location", "Producer name"]
}



def link_consumers_to_markets(data):
    """Link technosphere exchange inputs to markets and market groups.

    Should only be run after ``add_suppliers_to_markets``. Skips hard (activity) links, and exchanges which have already been linked.

    Add the field ``code`` to each exchange with the code of the linked market activity."""
    no_mg_filter = lambda x: x['type'] != "market group"
    ma_filter = lambda x: x['type'] == "market activity"
    ta_filter = lambda x: x['type'] == "transforming activity"
    markets_filter = lambda x: x['type'] in ("market activity", "market group")
    markets_mapping = dict(toolz.groupby(
        'reference product',
        filter(markets_filter, data)
    ))

    # Used only to resolve RoW for consumers
    ma_mapping = dict(toolz.groupby(
        'name',
        filter(ma_filter, data)
    ))
    ta_mapping = dict(toolz.groupby(
        'name',
        filter(ta_filter, data)
    ))

    def annotate(exc, ds):
        exc = annotate_exchange(exc, ds)
        exc['production volume'] = {'amount': production_volume(ds, 0)}
        return exc

    for ds in filter(no_mg_filter, data):
        # Only unlinked (not recycled content or direct linked) technosphere inputs
        loc = ds['location']

        if loc == 'RoW':
            if ds['type'] == 'transforming activity':
                dct = ta_mapping
            else:
                dct = ma_mapping
            consumer_row = topology.resolve_row(
                [x['location'] for x in dct[ds['name']]]
            )
        else:
            consumer_row = None

        def contains_wrapper(consumer, supplier, found, consumer_row, supplier_row):
            kwargs = {
                'parent': consumer,
                'child': supplier_row if supplier == 'RoW' else supplier,
                'subtract': found,
                'resolved_row': consumer_row if consumer == 'RoW' else None
            }
            return topology.contains(**kwargs)

        for exc in list(filter(unlinked, ds['exchanges'])):
            try:
                candidates = markets_mapping[exc['name']]
            except KeyError:
                if exc['name'] == 'refinery gas':
                    pass
                else:
                    raise MissingSupplier("No markets found for product {}".format(exc['name']))

            found, to_add = [], []

            markets = {x['location']: x for x in candidates if x['type'] == 'market activity'}
            market_groups = {x['location']: x for x in candidates if x['type'] == 'market group'}

            if 'RoW' in markets:
                supplier_row = topology.resolve_row(markets)
            else:
                supplier_row = set()

            together = set(markets).union(set(market_groups))
            ordered = topology.ordered_dependencies(
                [{'location': l} for l in together],
                supplier_row
            )

            for candidate in ordered:
                if contains_wrapper(loc, candidate, found, consumer_row, supplier_row):
                    found.append(candidate)
                    if candidate in markets:
                        to_add.append(markets[candidate])
                    else:
                        to_add.append(market_groups[candidate])
            if not found:
                # No market or market group within this location -
                # Find smallest market or market group which contains this activity
                for candidate in reversed(ordered):
                    if contains_wrapper(candidate, loc, found, supplier_row, consumer_row):
                        found.append(candidate)
                        if candidate in markets:
                            to_add.append(markets[candidate])
                        else:
                            to_add.append(market_groups[candidate])
                        break

            if len(to_add) == 1:
                obj = to_add[0]
                exc['code'] = obj['code']

                message = "Link complete input of {} '{}' from '{}' ({})"
                detailed.info({
                    'ds': ds,
                    'message': message.format(
                        exc['name'],
                        exc['amount'],
                        obj['name'],
                        obj['location']
                    ),
                    'function': 'link_consumers_to_markets'
                })
            else:
                ds['suppliers'] = [annotate(exc, obj) for obj in to_add]

                if not ds['suppliers']:
                    del ds['suppliers']
                    continue

                for e in ds['suppliers']:
                    logger.info({
                        'type': 'table element',
                        'data': (ds['name'], ds['location'], e['location'])
                    })
                    message = "Link consumption input of {} from '{}' ({})"
                    detailed.info({
                        'ds': ds,
                        'message': message.format(
                            exc['name'],
                            e['name'],
                            e['location']
                        ),
                        'function': 'link_consumers_to_markets'
                    })

                allocate_suppliers(ds, is_market=False, exc=exc)
                del ds['suppliers']
    return data

link_consumers_to_markets.__table__ = {
    'title': "Link market and market group suppliers to transforming activities.",
    'columns': ["Name", "Location", "Supplier Location"]
}


def log_and_delete_unlinked_exchanges(data):
    """Log and delete exchanges which haven't been linked."""
    for ds in data:
        for exc in filter(unlinked, ds['exchanges']):
            logger.info({
                'type': 'table element',
                'data': (ds['name'], exc['name'], exc['amount'])
            })
        ds['exchanges'] = [exc for exc in ds['exchanges'] if ds.get('code')]
    return data

log_and_delete_unlinked_exchanges.__table__ = {
    'title': "Exchanges which can't be linked",
    'columns': ["Name", "Flow", "Amount"]
}


def add_reference_product_codes(data):
    """Add ``code`` to single reference product exchange.

    Dataset must already have unique ``code``."""
    for ds in data:
        assert 'code' in ds
        rp = get_single_reference_product(ds)
        rp['code'] = ds['code']
    return data
