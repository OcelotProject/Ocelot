# -*- coding: utf-8 -*-
from ...errors import InvalidMultioutputDataset
from ..validation import check_single_output_activity
from .economic import economic_allocation
from .wastes import waste_treatment_allocation, recycling_allocation
import itertools


def no_allocation(dataset):
    return [dataset]


def choose_allocation_method(dataset):
    """Choose from among the following allocation methods:

    * combined production with byproducts
    * combined production without byproducts
    * constrained market
    * economic (including true value allocation)
    * recycling
    * waste treatment

    TODO: It feels strange to get reference product classification from the byproduct classification... this should at least be described a bit.

    The chosen allocation function is returned. For functions which don't need allocation, a dummy function (which does nothing) is returned. Note that all functions returned by this function must return a list of datasets.

    """
    reference_product_classifications = [exc['byproduct classification']
                                         for exc in dataset['exchanges']
                                         if exc['type'] == 'reference product'
                                         and exc['amount'] != 0]
    number_reference_products = len(reference_product_classifications)
    negative_reference_production = any(1 for exc in dataset['exchanges']
                                        if exc['type'] == 'reference product'
                                        and exc['amount'] < 0)
    allocatable_byproducts = any(1 for exc in dataset['exchanges']
                                 if exc['type'] == 'byproduct'
                                 and exc['byproduct classification'] == 'allocatable product'
                                 and exc['amount'] != 0)
    has_conditional_exchange = any(1 for exc in dataset['exchanges']
                                   if exc['type'] == 'byproduct'
                                   and exc['amount'] != 0
                                   and exc.get('conditional exchange'))

    # Validity checks
    if dataset['type'] == 'market group':
        assert number_reference_products == 1
        assert not allocatable_byproducts

    # No allocation needed
    if dataset['type'] == 'market group':
        return no_allocation
    elif number_reference_products == 1 and not allocatable_byproducts:
        return no_allocation
    elif dataset['type'] == 'market activity' and not has_conditional_exchange:
        # TODO: Why is there no allocation here? Still have more than one
        # reference product, or some byproducts?
        return no_allocation

    # Choose between available methods
    if dataset['type'] == 'market activity' and has_conditional_exchange:
        return 'constrained market'
    elif number_reference_products > 1:
        if allocatable_byproducts:
            return 'combined production with byproducts'
        else:
            return 'combined production without byproducts'
    elif negative_reference_production:
        assert len(set(reference_product_classifications)) == 1
        if reference_product_classifications[0] == 'waste':
            return waste_treatment_allocation
        else:
            return recycling_allocation
    else:
        return economic_allocation


def cutoff_allcation(data):
    """Do cutoff system model allocation."""
    return [check_single_output_activity(result)
            for ds in data
            for result in choose_allocation_method(ds)(ds)]
