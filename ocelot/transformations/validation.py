# -*- coding: utf-8 -*-
from .utils import allocatable_production
from ..errors import InvalidMultioutputDataset


def check_single_output_activity(dataset):
    """Check that the activity has exactly one reference product and no allocatable byproducts.

    Raise ``InvalidMultioutputDataset`` if any of these conditions are not met."""
    num_rp = sum(1 for exc in dataset['exchanges']
                 if exc['type'] == 'reference product')
    byproducts = any(1 for exc in dataset['exchanges']
                     if exc['type'] == 'byproduct'
                     and exc['byproduct classification'] == 'allocatable product')
    if num_rp != 1:
        raise InvalidMultioutputDataset("Found {} reference products".format(num_rp))
    if byproducts:
        raise InvalidMultioutputDataset("Found allocatable byproducts")
    return dataset
