# -*- coding: utf-8 -*-
from ..data_helpers import production_volume
from ..collection import Collection
from ..errors import UnresolvableActivityLink
from .utils import (
    allocatable_production,
    get_biggest_pv_to_exchange_ratio,
    nonproduction_exchanges,
)
from pprint import pformat
import logging

logger = logging.getLogger('ocelot')
detailed = logging.getLogger('ocelot-detailed')


def check_activity_link_validity(data):
    """Check whether hard (activity) links can be resolved correctly.

    In order to make sure we get the correct exchange, hard links must be to either a reference product exchange or an allocatable byproduct. We can safely ignore other exchanges, e.g. losses, with the same product name if this condition is met.

    Raises ``UnresolvableActivityLink`` if an exchange can't be found."""
    mapping = {ds['id']: ds for ds in data}
    link_iterator = (exc
                     for ds in data
                     for exc in ds['exchanges']
                     if exc.get("activity link"))
    for link in link_iterator:
        ds = mapping[link['activity link']]
        found = [exc
                 for exc in allocatable_production(ds)
                 if exc['name'] == link['name']]
        if len(found) == 1:
            continue
        elif len(found) > 1:
            message = "Found multiple candidates for activity link:\n{}\nTarget dataset:\n{}"
            raise UnresolvableActivityLink(message.format(pformat(link), ds['filepath']))
        else:
            message = "Found no candidates for activity link:\n{}\nTarget dataset:\n{}"
            raise UnresolvableActivityLink(message.format(pformat(link), ds['filepath']))
    return data


def add_hard_linked_production_volumes(data):
    """Add information to target datasets about subtracted production volume.

    Production volumes from hard (activity) links are subtracted from the total production volume of transforming or market activities. The amount to subtract is added to a new field in the production volume, ``subtracted activity link volume``.

    This should be run after the validity check ``check_activity_link_validity``.

    Production volumes in the target dataset are used to indicate relative contributions to markets; some datasets have their entire production consumed by hard links, and therefore would not contribute anything to market datasets.

    Example input:

    .. code-block:: python

        [{
            'id': 'link to me',
            'exchanges': [{
                'name': 'François',
                'production volume': {'amount': 100},
                'type': 'reference product',
            }]
        }, {
            'id': 'not useful',
            'exchanges': [{
                'activity link': 'link to me',
                'amount': 2,
                'name': 'François',
                'type': 'from technosphere',
            }, {
                'amount': 5,
                'production volume': {'amount': 100},
                'type': 'reference product',
            }]
        }]

    And corresponding output:

    .. code-block:: python

        [{
            'id': 'link to me',
            'exchanges': [{
                'name': 'François',
                'production volume': {
                    'amount': 100,
                    'subtracted activity link volume': 2 * 100 / 5  # <- This is added
                },
                'type': 'reference product',
            }],
        }, {
            'id': 'not useful',
            'exchanges': [{
                'activity link': 'link to me',
                'amount': 2,
                'name': 'François',
                'type': 'from technosphere',
            }, {
                'amount': 5,
                'production volume': {'amount': 100},
                'type': 'reference product',
            }],
        }]

    """
    mapping = {ds['id']: ds for ds in data}
    for ds in data:
        for exc in (e for e in ds['exchanges'] if e.get('activity link')):
            target = mapping[exc['activity link']]

            # Find the allocatable production exchange referenced by this
            # specific hard link. This is before allocation, so there can be
            # more than one production exchange.
            found = [obj
                     for obj in allocatable_production(target)
                     if obj['name'] == exc['name']]
            assert len(found) == 1
            hard_link = found[0]

            # From the dataset (`ds`) which is the origin of the hard link, we
            # only have a relative amount. But this datasets could be
            # multioutput. So to get the absolute amount of PV subtracted, we
            # need to translate relative to absolute amount. This value does
            # this in the `ds` frame of reference
            scale = get_biggest_pv_to_exchange_ratio(ds)

            message = "Subtracting activity link: {:.4g} (out of {:.4g}) from {} | {}"
            detailed.info({
                'ds': target,
                'message': message.format(
                    exc['amount'] * scale,
                    hard_link['production volume']['amount'],
                    ds['name'],
                    ds['location'],
                ),
                'function': 'add_hard_linked_production_volumes',
            })

            hard_link['production volume']["subtracted activity link volume"] = (
                hard_link['production volume'].get(
                    "subtracted activity link volume", 0
                ) + exc['amount'] * scale
            )
    return data


manage_activity_links = Collection(
    "Resolve hard (activity) links",
    check_activity_link_validity,
    add_hard_linked_production_volumes,
)


def update_activity_link_parent_child(data):
    """Update exchange activity links from parent to child (i.e. the current) dataset.

    Correct an error in ecoinvent master data production.

    In a few cases, an exchange in a child dataset includes an ``activityLink``
    to the parent dataset, from which the dataset is derived. For example, the
    parent global dataset ``market for medium voltage electricity`` has a child
    dataset actualized for Iceland (IS). The input for losses due to voltage
    conversion and transmission still had an ``activityLink`` to the global
    dataset, however. This function redirects that activity link to the child
    dataset."""
    for ds in data:
        parent = ds['parent']
        if not parent:
            continue
        for exc in nonproduction_exchanges(ds):
            if exc.get('activity link') == parent:
                exc['activity link'] = ds['id']
                logger.info({
                    'type': 'table element',
                    'data': (ds['name'], ds['location'], exc['amount']),
                })
    return data

update_activity_link_parent_child.__table__ = {
    'title': 'Switch activity links to child dataset',
    'columns': ['Name', 'Location', 'Amount']
}
