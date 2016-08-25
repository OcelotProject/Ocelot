# -*- coding: utf-8 -*-
from ...collection import Collection
from ...errors import InvalidMultioutputDataset
from ...wrapper import TransformationWrapper
from .combined import combined_production, combined_production_with_byproducts
from .economic import economic_allocation
from .markets import constrained_market_allocation
from .utils import delete_allocation_method
from .validation import valid_no_allocation_dataset
from .wastes import waste_treatment_allocation, recycling_allocation
import itertools


@valid_no_allocation_dataset
def no_allocation(dataset):
    """No-op for single output dataset.

    Performs a validity check to make sure that there is only one reference product and no allocatable byproducts."""
    return [dataset]


def choose_allocation_method(dataset):
    """Choose from among the following allocation methods:

    * combined production
    * combined production with byproducts
    * constrained market
    * economic (including true value allocation)
    * recycling
    * waste treatment

    TODO: It feels strange to get reference product classification from the byproduct classification... this should at least be described a bit.

    The chosen allocation function is returned. For functions which don't need allocation, a dummy function (which does nothing) is returned. Note that all functions returned by this function must return a list of datasets.

    """
    reference_product_classifications = [exc.get('byproduct classification')
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
                                   and exc.get('conditional exchange'))

    if number_reference_products == 1 and not allocatable_byproducts:
        return None
    elif dataset['type'] == 'market group':
        return None
    elif dataset['type'] == 'market activity':
        if has_conditional_exchange:
            return "constrained market"
        else:
            return None
    elif number_reference_products > 1:
        if allocatable_byproducts:
            return "combined production with byproducts"
        else:
            return "combined production"
    elif negative_reference_production:
        # TODO: Should be part of a validation function
        assert len(set(reference_product_classifications)) == 1
        if reference_product_classifications[0] == 'waste':
            return "waste treatment"
        else:
            return "recycling"
    else:
        return "economic"


def label_allocation_method(data):
    """Add ``allocation method`` attribute to each dataset with the chosen allocation function."""
    for ds in data:
        ds['allocation method'] = choose_allocation_method(ds)
    return data


ALLOCATION_METHODS = {
    None: no_allocation,
    "economic": economic_allocation,
    "recycling": recycling_allocation,
    "waste treatment": waste_treatment_allocation,
    "combined production": combined_production,
    "combined production with byproducts": combined_production_with_byproducts,
    "constrained market": constrained_market_allocation,
}


def create_allocation_filter(label):
    """Return a function that checks where the dataset allocation method is ``label``.

    Previous approach using lambda broke somewhere deep and mysterious..."""
    def allocation_method_filter(ds):
        return ds['allocation method'] == label
    return allocation_method_filter


cutoff_allocation = Collection(
    label_allocation_method,
    *[TransformationWrapper(func,
                            create_allocation_filter(label))
      for label, func in ALLOCATION_METHODS.items()],
    TransformationWrapper(delete_allocation_method),
)
