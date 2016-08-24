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
def valid_economic_activity(wrapped, instance, args, kwargs):
    """Check to make sure the activity meets the assumptions for economic allocation.

    * All allocatable products must have a price.

    """
    dataset = kwargs.get('dataset') or args[0]
    for exchange in allocatable_production(dataset):
        if get_numerical_property(exchange, 'price') is None:
            message = "No price given for exchange:\n{}\nIn dataset:\n{}"
            raise InvalidExchange(message.format(pformat(exchange), pformat(dataset)))
    return wrapped(*args, **kwargs)


@wrapt.decorator
def valid_recycling_activity(wrapped, instance, args, kwargs):
    """Check to make sure the activity meets the assumptions for recycling allocation.

    * There is exactly one reference product exchange with a positive production amount
    * There is at least one byproduct exchange.

    """
    dataset = kwargs.get('dataset') or args[0]
    rp = get_single_reference_product(dataset)
    if not rp['amount'] < 0:
        message = "Reference product exchange amount shouldn't be positive:\n{}"
        raise InvalidExchange(message.format(pformat(dataset)))
    if not any(exc for exc in dataset['exchanges']
               if exc['type'] == 'byproduct'
               and exc['byproduct classification'] == 'allocatable product'):
        message = "No allocatable byproducts in recycling activity:\n{}"
        raise InvalidExchange(message.format(pformat(dataset)))
    return wrapped(*args, **kwargs)


@wrapt.decorator
def valid_waste_treatment_activity(wrapped, instance, args, kwargs):
    """Check to make sure the activity meets the assumptions for waste treatment allocation.

    * There is a single reference product exchange with a negative amount and ``byproduct classification`` of ``waste``.

    """
    dataset = kwargs.get('dataset') or args[0]
    rp = get_single_reference_product(dataset)
    if rp.get('byproduct classification') != 'waste':
        message = ("Wrong byproduct classification for waste treatment "
            "reference product:\n{}\nIn dataset:\n{}")
        raise InvalidExchange(message.format(pformat(exchange), pformat(dataset)))
    if not rp['amount'] < 0:
        message = ("Waste treatment ref. product exchange amount must be "
            "negative:\n{}\nIn dataset:\n{}")
        raise InvalidExchange(message.format(pformat(exchange), pformat(dataset)))
    return wrapped(*args, **kwargs)


@wrapt.decorator
def valid_combined_production_activity(wrapped, instance, args, kwargs):
    """Check to make sure the activity meets the assumptions for combined production allocation.

    * Each refernce product exchange must be a variable name, so that the amount of inputs can vary depending on whether that reference product is chosen in subdivision.

    """
    dataset = kwargs.get('dataset') or args[0]
    for exc in dataset['exchanges']:
        if (exc['type'] == 'reference product'
            and exc['amount']
            and not exc.get('variable')):
            message = ("Ref. product exchange in combined production must have"
                " variable name:\n{}\nIn dataset:\n{}")
            raise InvalidExchange(message.format(pformat(exc), pformat(dataset)))
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
