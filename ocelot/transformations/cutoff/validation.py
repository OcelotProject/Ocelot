# -*- coding: utf-8 -*-
from ..utils import (
    allocatable_production,
    get_numerical_property,
    get_single_reference_product,
)
from ...errors import InvalidExchange
from pprint import pformat
import wrapt


@wrapt.decorator
def valid_recycling_activity(wrapped, instance, args, kwargs):
    """Check to make sure the activity meets the assumptions for recycling allocation.

    * There is exactly one reference product exchange with a positive production amount
    * There is at least one byproduct exchange.

    """
    dataset = kwargs.get('dataset') or args[0]
    rp = get_single_reference_product(dataset)
    if not rp['amount'] > 0:
        message = "Reference product exchange amount not greater than 0:\n{}"
        raise InvalidExchange(message.format(pformat(dataset)))
    if not any(exc for exc in dataset['exchanges']
               if exc['type'] == 'byproduct'
               and exc['byproduct classification'] == 'allocatable'):
        message = "No allocatable byproducts in recycling activity:\n{}"
        raise InvalidExchange(message.format(pformat(dataset)))
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
