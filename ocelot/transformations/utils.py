# -*- coding: utf-8 -*-


def extract_products_as_tuple(dataset):
    return tuple(sorted([exc['name']
                  for exc in dataset['exchanges']
                  if exc['type'] == 'reference product']))


def activity_grouper(dataset):
    return (dataset['name'], extract_products_as_tuple(dataset))


def iterate_exchanges(datasets):
    """Iterate over all exchanges in all datasets"""
    for ds in datasets:
        for exc in ds['exchanges']:
            yield exc


def production_exchanges(dataset):
    """Return exchanges whose type is ``reference product`` or ``byproduct``"""
    for exc in dataset['exchanges']:
        if exc['type'] in ('reference product', 'byproduct'):
            yield exc


def get_numerical_property(exchange, property_name):
    """Get ``amount`` value for property ``property_name``.

    Returns a float or ``None``."""
    for prop in exchange.get("properties", []):
        if prop['name'] == property_name:
            return prop['amount']
