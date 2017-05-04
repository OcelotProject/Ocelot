# -*- coding: utf-8 -*-
from ..collection import Collection
from ..errors import UnresolvableActivityLink
from .utils import allocatable_production, get_biggest_pv_to_exchange_ratio
from pprint import pformat


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
            found = [obj
                     for obj in allocatable_production(target)
                     if obj['name'] == exc['name']]
            assert len(found) == 1
            hard_link = found[0]

            scale = get_biggest_pv_to_exchange_ratio(ds)

            hard_link['production volume']["subtracted activity link volume"] = (
                hard_link['production volume'].get(
                    "subtracted activity link volume", 0
                ) + exc['amount'] * scale
            )
    return data


manage_activity_links = Collection(
    check_activity_link_validity,
    add_hard_linked_production_volumes,
)
