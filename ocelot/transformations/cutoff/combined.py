# -*- coding: utf-8 -*-
from ... import toolz
from ..utils import (
    activity_grouper,
    allocatable_production,
    get_single_reference_product,
    nonreference_product,
    remove_exchange_uncertainty,
)
from ..parameterization import recalculate
from .economic import economic_allocation
from .validation import valid_merge_datasets
from copy import deepcopy


###
### Note: Recalculation of parameters must be manually tested
### py.test and asteval both mess with the AST, leading to recursion errors
### Run `python tests/manual/run_all_ci.py` to test parameter recalculation
### The CI systems run the manual tests as well
###


def nonzero_reference_product_exchanges(dataset):
    """Return generator of all nonzero reference product exchanges"""
    return (exc for exc in dataset['exchanges']
            if exc['type'] == 'reference product'
            and exc['amount'])


def selected_product(exc):
    """Modify a production exchange to fix its numeric value.

    * Sets undertainty to no uncertainty
    * Deletes formula to prevent any changes in parameter evaluations.

    """
    if 'formula' in exc:
        del exc['formula']
    return remove_exchange_uncertainty(exc)


def combined_production(dataset):
    """Perform subdivision of combined production activities.

    Combined production activities can vary the production of several reference products. As such, subdivision can be performed, and no allocation is needed. However, allocation may be needed for the resulting datasets, which may have byproducts.

    Subdivision assumes that the datasets are parameterized. Each reference product exchange should be a variable:

    .. code-block:: python

        {
            'type': 'reference production',
            'amount': 0.5,
            'variable': 'a_variable_name'
        }

    This variable can be referred to in other exchanges or parameters to determine the amounts of technosphere input or biosphere outputs.

    Subdivision is performed by iterating over the non-zero reference products, making a copy of the dataset, and setting the amount of all **other** reference product exchange variables to zero. We then recalculate the formulas and variables, and get the inputs needed for the production of only one reference product.

    Returns a list of new datasets."""
    new_datasets = []
    for exc in nonzero_reference_product_exchanges(dataset):
        new_ds, rp = deepcopy(dataset), deepcopy(exc)
        new_ds['exchanges'] = [selected_product(rp)] + \
            [nonreference_product(obj)
             for obj in nonzero_reference_product_exchanges(new_ds)
             if obj != exc] + \
            [deepcopy(obj) for obj in dataset['exchanges']
             if obj['type'] != 'reference product']
        new_datasets.append(recalculate(new_ds))
    return new_datasets


def combined_production_without_products(dataset):
    """A special case of combined production allocation where there are no allocatable products.

    This special case occurs only once in ecoinvent 3.2, in the dataset ``treatment of manure and biowaste by anaerobic digestion``, which produces the following reference products:

    """
    print(dataset['name'])
    print(dataset['filepath'])
    return [dataset]


def add_exchanges(to_dataset, from_dataset):
    """Add exchange amounts in ``from_dataset`` to ``to_dataset``.

    Uses ``id`` to uniquely identify each exchange.

    Removes uncertainty from reference product exchanges.

    Returns a modified ``to_dataset``."""
    lookup = {exc['id']: exc['amount'] for exc in from_dataset['exchanges']}
    for exc in to_dataset['exchanges']:
        exc['amount'] += lookup.get(exc['id'], 0)
        if exc['type'] == 'reference product':
            # No uncertainty but still min and max should be updated
            remove_exchange_uncertainty(exc)
    return to_dataset


@valid_merge_datasets
def merge_byproducts(data):
    """Generator which merges datasets which have the same reference product.

    Add exchange values together.

    Used after economic allocation, so there should be no allocatable byproducts remaining.

    Don't need to change reference production volumes because they are unchanged from the original multioutput dataset.

    TODO: Handle uncertainty for inputs by creating new parameters and adding them in exchange formulas?

    TODO: Parameter values can be different in merged datasets, but can't just be added. Maybe also create new parameters (but not clear how)? Or easier just to delete all parameterization...

    Yields a new dataset."""

    for group in toolz.groupby(activity_grouper, data).values():
        parent = group[0]
        for child in group[1:]:
            parent = add_exchanges(parent, child)
        yield parent


def combined_production_with_byproducts(dataset):
    """Subdivide, allocate, and then merge combined production datasets with byproducts.

    If a dataset has two reference products, A and B, and a byproduct C, then subdivision will create two new datasets, A' and B'. Each of these will have C as a byproduct, so economic allocation is performed on both A' and B', giving a total of four datasets: A', B', C1 (from A'), and C2 (from B'). However, C1 and C2 are producing the same product, so they need to be merged to make one C dataset.

    Returns a list of new datasets."""
    new_datasets = [ds
                    for subdivided in combined_production(dataset)
                    for ds in economic_allocation(subdivided)]
    return list(merge_byproducts(new_datasets))
