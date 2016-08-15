# -*- coding: utf-8 -*-
from ..errors import InvalidExchange
from ..utils import get_single_reference_product
from pprint import pformat
import wrapt


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
               if (exc['type'] == 'byproduct' and
               exc['byproduct classification'] == 'allocatable'):
        message = "No allocatable byproducts in recycling activity:\n{}"
        raise InvalidExchange(message.format(pformat(dataset)))
    return wrapped(*args, **kwargs)
