# -*- coding: utf-8 -*-
import logging


TECHNOLOGY_LEVEL_HIERARCHY = (
    "new",
    "modern",
    "current",
    "old",
    "outdated",
)


def prune_suppliers_by_technology_level(data):
    """Reduce the list of ``suppliers`` to those with the highest technology level."""
    MARKETS = ("market activity", "market group")
    for ds in (o for o in data if o['type'] in MARKETS):
        if not ds.get('suppliers'):
            continue

        # TODO: In theory we need to check if market is decreasing,
        # in which case we would apply the hierarchy in reverse order.
        # But this information is not obviously accessible.

        for level in TECHNOLOGY_LEVEL_HIERARCHY:
            suppliers = [o for o in ds['suppliers']
                         if o['technology level'] == level]
            if suppliers:
                break
        assert suppliers, "No suppliers had a suitable technology level"
        ds['suppliers'] = suppliers
    return data
