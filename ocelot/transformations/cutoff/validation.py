# -*- coding: utf-8 -*-
from ..utils import (
    allocatable_production,
    get_numerical_property,
    get_single_reference_product,
)
from ..validation import check_single_output_activity
from ...errors import InvalidExchange
from pprint import pformat
import wrapt


@wrapt.decorator
def valid_no_allocation_dataset(wrapped, instance, args, kwargs):
    """Check to make sure the activity has one reference product and no byproducts"""
    dataset = kwargs.get('dataset') or args[0]
    check_single_output_activity(dataset)
    return wrapped(*args, **kwargs)


@wrapt.decorator
def valid_merge_datasets(wrapped, instance, args, kwargs):
    """Datasets to be merged based on common reference products should have no allocatable byproducts"""
    data = kwargs.get('data') or args[0]
    for ds in data:
        if any(1 for exc in ds['exchanges']
               if exc['type'] == 'byproduct'
               and exc['classification'] == 'allocatable product'):
            raise InvalidExchange("Exchanges with byproducts passes to ``merge_byproducts``")
    return wrapped(*args, **kwargs)


@wrapt.decorator
def valid_economic_activity(wrapped, instance, args, kwargs):
    """Check to make sure the activity meets the assumptions for economic allocation.

    * All allocatable products must have a positive price.
    * All allocatable products must have a positive exchange amount.

    """
    dataset = kwargs.get('dataset') or args[0]
    for exchange in allocatable_production(dataset):
        if get_numerical_property(exchange, 'price') is None:
            message = "No price given for exchange:\n{}\nIn dataset:\n{}"
            raise InvalidExchange(message.format(pformat(exchange), pformat(dataset['filepath'])))
        elif get_numerical_property(exchange, 'price') < 0:
            message = "Price must be greater than zero:\n{}\nIn dataset:\n{}"
            raise InvalidExchange(message.format(pformat(exchange), pformat(dataset['filepath'])))
        elif exchange['amount'] < 0:
            message = "Exchange amount must be greater than zero:\n{}\nIn dataset:\n{}"
            raise InvalidExchange(message.format(pformat(exchange), pformat(dataset['filepath'])))
    return wrapped(*args, **kwargs)


@wrapt.decorator
def valid_recycling_activity(wrapped, instance, args, kwargs):
    """Check to make sure the activity meets the assumptions for recycling allocation.

    * There is exactly one reference product exchange with a positive production amount
    * There is at least one byproduct exchange with classification ``allocatable byproduct``.
    * Each of these allocatable byproducts must meet the requirements for economic allocation.

    """
    dataset = kwargs.get('dataset') or args[0]
    rp = get_single_reference_product(dataset)
    if not rp['amount'] < 0:
        message = "Reference product exchange amount shouldn't be positive:\n{}"
        raise InvalidExchange(message.format(pformat(dataset['filepath'])))

    allocatable_byproducts = (
        exc
        for exc in dataset['exchanges']
        if exc['type'] == 'byproduct'
        and exc['classification'] == 'allocatable product'
    )
    if not any(allocatable_byproducts):
        message = "No allocatable byproducts in recycling activity:\n{}"
        raise InvalidExchange(message.format(pformat(dataset['filepath'])))
    return wrapped(*args, **kwargs)


@wrapt.decorator
def valid_waste_treatment_activity(wrapped, instance, args, kwargs):
    """Check to make sure the activity meets the assumptions for waste treatment allocation.

    * There is a single reference product exchange with a negative amount and ``classification`` of ``waste``.

    """
    dataset = kwargs.get('dataset') or args[0]
    rp = get_single_reference_product(dataset)
    if rp.get('classification') != 'waste':
        message = ("Wrong byproduct classification for waste treatment "
            "reference product:\n{}\nIn dataset:\n{}")
        raise InvalidExchange(message.format(pformat(rp), dataset['filepath']))
    if not rp['amount'] < 0:
        message = ("Waste treatment ref. product exchange amount must be "
            "negative:\n{}\nIn dataset:\n{}")
        raise InvalidExchange(message.format(pformat(rp), dataset['filepath']))
    return wrapped(*args, **kwargs)


def ready_for_market_linking(data):
    """All transforming activities must have exactly one reference product.

    * Datasets must have the attribute ``reference product``
    * Datasets must have one reference product exchange.

    Will raise ``ValueError`` or ``InvalidMultioutputDataset`` if these conditions aren't met.

    """
    for ds in data:
        if ds['type'] == 'transforming activity':
            assert get_single_reference_product(ds)
            if not ds.get('reference product'):
                raise ValueError("Dataset doesn't have ``reference product``")
    return data
