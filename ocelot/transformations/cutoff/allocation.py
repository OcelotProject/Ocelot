# -*- coding: utf-8 -*-
from ...collection import Collection
from ...wrapper import TransformationWrapper
from ..utils import allocatable_production
from .combined import (
    combined_production,
    combined_production_with_byproducts,
    combined_production_without_products,
)
from .economic import economic_allocation
from .markets import constrained_market_allocation
from .utils import delete_allocation_method
from .validation import valid_no_allocation_dataset
from .wastes import waste_treatment_allocation, recycling_allocation
import logging


@valid_no_allocation_dataset
def no_allocation(dataset):
    """No-op for single output dataset.

    Performs a validity check to make sure that there is only one reference product and no allocatable byproducts."""
    return [dataset]


def choose_allocation_method(dataset):
    """Choose from among the following allocation methods:

    * no allocation
    * combined production
    * combined production with byproducts
    * constrained market
    * economic (including true value) allocation
    * recycling
    * waste treatment

    The chosen allocation function is returned as a string.

    The choice is made using the following decision tree:

    If the dataset is a market group:
        * **no allocation**

    If the dataset has only one reference product and no allocatable byproducts:
        * **no allocation**

    If the dataset is a market activity:
        * and has a conditional exchange: **constrained market**,
        * otherwise: **no allocation**

    A conditional exchange is an exchange with the following properties:

    * The exchange amount is negative
    * The exchange has a hard (activity) link
    * The exchange is a byproduct

    Conditional exchanges are used in the consequential system model.

    If there is more than one reference product,
        * and there are allocatable byproducts: **combined production with byproducts**,
        * otherwise: **combined production**.

    If the reference production exchange has a negative amount, meaning that this dataset is a treatment service that consumes instead of producing something:
        * If the reference product has the classification ``waste``: **waste treatment**
        * Otherwise: **recycling**

    If no of the above apply:
        * **economic**

    Economic allocation uses "true value" properties whenever they are present.

    """
    reference_product_classifications = [exc.get('byproduct classification')
                                         for exc in dataset['exchanges']
                                         if exc['type'] == 'reference product'
                                         and exc['amount'] != 0]
    number_reference_products = len(reference_product_classifications)
    negative_reference_production = any(1 for exc in dataset['exchanges']
                                        if exc['type'] == 'reference product'
                                        and exc['amount'] < 0)
    allocatable_byproducts = any(1 for exc in allocatable_production(dataset)
                                 if exc['type'] == 'byproduct'
                                 and exc['amount'] != 0)
    allocatable_products = any(1 for exc in allocatable_production(dataset)
                               if exc['type'] == 'reference product'
                               and exc.get('byproduct classification') == 'allocatable product')
    has_conditional_exchange = any(1 for exc in dataset['exchanges']
                                   if exc.get('conditional exchange'))

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
        if not allocatable_products:
            return "combined production without products"
        elif allocatable_byproducts:
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


ALLOCATION_METHODS = (
    (None, no_allocation),
    ("economic", economic_allocation),
    ("constrained market", constrained_market_allocation),
    ("recycling", recycling_allocation),
    ("waste treatment", waste_treatment_allocation),
    ("combined production without products", combined_production_without_products),
    ("combined production", combined_production),
    ("combined production with byproducts", combined_production_with_byproducts),
)


def label_allocation_method(data):
    """Add ``allocation method`` attribute to each dataset with the chosen allocation function."""
    for ds in data:
        ds['allocation method'] = choose_allocation_method(ds)
    for label, _ in ALLOCATION_METHODS:
        logging.info({
            'type': 'table element',
            'data': (
                str(label),
                sum(1 for ds in data if ds['allocation method'] == label)
            ),
        })
    return data

label_allocation_method.__table__ = {
    'title': 'Label allocation method types',
    'columns': ["Allocation", "Count"]
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
      for label, func in ALLOCATION_METHODS[1:]],
    delete_allocation_method,
)
