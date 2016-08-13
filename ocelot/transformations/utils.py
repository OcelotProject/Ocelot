# -*- coding: utf-8 -*-
import pandas as pd


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


def allocatable_production(dataset):
    """Return exchanges whose type is ``reference product``, or ``byproduct`` and whose ``byproduct classification`` is ``allocatable``."""
    for exc in dataset['exchanges']:
        if exc['type'] =='reference product':
            yield exc
        elif (exc['type'] == 'byproduct' and
              exc['byproduct classification'] == 'allocatable'):
            yield exc


def get_numerical_property(exchange, property_name):
    """Get ``amount`` value for property ``property_name``.

    Returns a float or ``None``."""
    for prop in exchange.get("properties", []):
        if prop['name'] == property_name:
            return prop['amount']


def get_property_by_name(exchange, name):
    for prop in exchange.get("properties", []):
        if prop['name'] == name:
            return prop
    return {}


def exchanges_as_dataframe(dataset):
    data = []
    for exc in allocatable_production(dataset):
        data.append({
            'name': exc['name'],
            'amount': exc['amount'],
            'type': exc['type'],
            'price': get_property_by_name(exc, 'price').get('amount', 0),
            'has true value': bool(get_property_by_name(exc, 'true value relation')),
            'true value': get_property_by_name(exc, 'true value relation').get(
                'amount', 0),
        })
    df = pd.DataFrame(data)
    df['revenue'] = df['price'] * df['amount']
    return df


def update_amounts_from_dataframe(dataset, df, field="amount"):
    pass
