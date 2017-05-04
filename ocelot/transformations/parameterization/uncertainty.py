# -*- coding: utf-8 -*-
from ..uncertainty import get_uncertainty_class
from ..utils import iterate_all_uncertainties
import logging


def repair_all_uncertainty_distributions(data):
    """Repair all uncertainty distributions.

    Uses distribution-specific ``repair`` methods."""
    for ds in data:
        for obj in iterate_all_uncertainties(ds):
            if obj.get('uncertainty'):
                # TODO: Add detailed log message
                get_uncertainty_class(obj).repair(obj)
    return data
