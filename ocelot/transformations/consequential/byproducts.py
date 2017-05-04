# -*- coding: utf-8 -*-
from ...errors import MissingAlternativeProducer


def ensure_byproducts_have_alternative_production(data):
    """Each byproduct must have an alternative producer that it can substitute.

    Raises ``MissingAlternativeProducer`` if this condition is not met."""
    products = {exc['name'] for ds in data for exc in ds['exchanges']
                if exc['type'] == 'reference product'}
    byproducts = {exc['name'] for ds in data for exc in ds['exchanges']
                  if exc['type'] == 'byproduct'}
    missing = byproducts.difference(products)
    if missing:
        message = "Can't find alternative producers for the following:\n\t{}"
        raise MissingAlternativeProducer(message.format("\n\t".join(missing)))
    return data
