# -*- coding: utf-8 -*-
from ..utils import choose_reference_product_exchange


def apply_allocation_factors(dataset, factors):
    """Apply allocation factors given in ``factors`` to ``dataset``.

    ``dataset`` is a normal activity dataset. ``factors`` has the data format: ``[(allocation factor, chosen reference product exchange)]``.

    Returns a list of ``len(factors)`` new datasets."""
    return [
        choose_reference_product_exchange(dataset, exc, scale)
        for scale, exc in factors
    ]


def delete_allocation_method(dataset):
    """Delete key ``allocation method`` if present"""
    if "allocation method" in dataset:
        del dataset["allocation method"]
    return [dataset]
