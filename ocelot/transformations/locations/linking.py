# -*- coding: utf-8 -*-
from . import topology, RC_STRING
from ... import toolz
from ...errors import UnresolvableActivityLink, OverlappingMarkets
from ..utils import get_single_reference_product
import logging


unlinked = lambda x: x['type'] == 'from technosphere' and not x.get('code')


def actualize_activity_links(data):
    """Add ``code`` field to activity links."""
    mapping = toolz.groupby("id", data)
    link_iterator = (exc
                     for ds in data
                     for exc in ds['exchanges']
                     if exc.get("activity link"))
    for link in link_iterator:
        references = [ds
                      for ds in mapping[link['activity link']]
                      if ds['reference product'] == link['name']]
        if len(references) != 1:
            # TODO: Resolve all sorts of special cases...
            # Just logging for now
            logging.info({
                'type': 'table element',
                'data': (link['activity link'], link['name'], link['amount'])
            })
            continue
            # raise UnresolvableActivityLink(message.format(link['activity link']))
        link['code'] = references[0]['code']
    return data

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
            logging.info({
                'type': 'table element',
                'data': (ds['name'], exc['name'], ds['location'], sup['name'])
            })
    return data

link_consumers_to_recycled_content_activities.__table__ = {
    'title': 'Link input exchanges to cutoff recycled content producers',
    'columns': ["Consumer name", "Product", "Location", "Producer name"]
}


def link_consumers_to_regional_markets(data):
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
                # TODO: Too many links, create separate log
                # logging.info({
                #     'type': 'table element',
                #     'data': (exc['name'], ds['location'],
                #              sup['name'], sup['location'])
                # })
            else:
                # Shouldn't be possible - markets shouldn't overlap
                message = "Multiple markets contain {} in {}:\n{}"
                raise OverlappingMarkets(message.format(
                    exc['name'],
                    ds['location'],
                    [x['location'] for x in contained])
                )
    return data

# link_consumers_to_regional_markets.__table__ = {
#     'title': 'Link input exchanges to regional supply market',
#     'columns': ["Product", "Location", "Market name", "Market location"]
# }


def link_consumers_to_global_markets(data):
    """Link technosphere exchange inputs to ``GLO`` or ``RoW`` markets.

    Add the field ``code`` to each exchange with the code of the linked market activity."""
    filter_func = lambda x: x['type'] == "market activity"
    market_mapping = toolz.groupby(
        'reference product',
        filter(filter_func, data)
    )

    for ds in data:
        for exc in filter(unlinked, ds['exchanges']):
            try:
                contributors = [
                    x for x in market_mapping[exc['name']]
                    if x['location'] in ("GLO", "RoW")]
                assert len(contributors) == 1
            except (KeyError, AssertionError):
                continue

            sup = contributors[0]
            exc['code'] = sup['code']
            # TODO: Too many links, create separate log
            # logging.info({
            #     'type': 'table element',
            #     'data': (sup['name'], ds['name'], exc['name'], ds['location'])
            # })
    return data

# link_consumers_to_global_markets.__table__ = {
#     'title': 'Link input exchanges to correct supplying market',
#     'columns': ["Market name", "Activity name", "Product", "Location"]
# }


def log_unlinked_exchanges(data):
    """Log exchanges which haven't been linked."""
    for ds in data:
        for exc in filter(unlinked, ds['exchanges']):
            logging.info({
                'type': 'table element',
                'data': (ds['name'], exc['name'], exc['amount'])
            })
    return data

log_unlinked_exchanges.__table__ = {
    'title': "Exchanges which can't be linked",
    'columns': ["Name", "Flow", "Amount"]
}

