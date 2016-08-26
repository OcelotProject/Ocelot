# -*- coding: utf-8 -*-
from ..collection import Collection
from ..errors import UnresolvableActivityLink
from .utils import allocatable_production, get_numerical_property
from .validation import ensure_production_exchanges_have_production_volume
from pprint import pformat
import logging


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

    TODO: Why does it matter that production volumes are subtracted?"""
    mapping = {ds['id']: ds for ds in data}
    for ds in data:
        for exc in (e for e in ds['exchanges'] if e.get('activity link')):
            target = mapping[exc['activity link']]
            found = [obj
                     for obj in allocatable_production(target)
                     if obj['name'] == exc['name']]
            assert len(found) == 1
            hard_link = found[0]

            # Get a reference product for ``exc`` - doesn't matter which one.
            ref_prod = [exc for exc in ds['exchanges']
                        if exc['type'] == 'reference product'][0]

            # Then calculate the amount to subtract - the exchange amount times
            # the ratio of ref. prod. prouction volume to its exchange amount.
            pv = (ref_prod['production volume']['amount']
                  / ref_prod['amount'] * exc['amount'])
            hard_link['production volume']["subtracted activity link volume"] = (
                hard_link['production volume'].get(
                    "subtracted activity link volume", 0
                ) + pv
            )
    return data


manage_activity_links = Collection(
    ensure_production_exchanges_have_production_volume,
    check_activity_link_validity,
    add_hard_linked_production_volumes,
)
