# -*- coding: utf-8 -*-
import pandas as pd


def iterate_exchanges(data):
    """Return generator of all exchanges in a database"""
    return (exc for ds in data for exc in ds['exchanges'])


def allocatable_production(dataset):
    """Return generator of production exchanges for a dataset.

    Production exchanges either:

    * Have type ``reference product``, or
    * Have type ``byproduct`` and ``byproduct classification`` is ``allocatable``

    """
    for exc in dataset['exchanges']:
        if exc['type'] =='reference product':
            yield exc
        elif (exc['type'] == 'byproduct' and
              exc['byproduct classification'] == 'allocatable'):
            yield exc


def extract_products_as_tuple(dataset):
    """Return names of all products as a sorted tuple.

    Products are chosen using ``allocatable_production``."""
    return tuple(sorted([exc['name'] for exc in allocatable_production(dataset)]))


def activity_grouper(dataset):
    """Return tuple of dataset name and products.

    Products are chosen using ``extract_products_as_tuple``."""
    return (dataset['name'], extract_products_as_tuple(dataset))


def get_numerical_property(exchange, property_name):
    """Get ``amount`` value for property ``property_name`` in exchange ``exchange``.

    Returns a float or ``None``."""
    for prop in exchange.get("properties", []):
        if prop['name'] == property_name:
            return prop['amount']


def get_property_by_name(exchange, name):
    """Get property object with name ``name`` from exchange ``exchange``.

    Returns an empty dictionary if the property named ``name`` is not found."""
    for prop in exchange.get("properties", []):
        if prop['name'] == name:
            return prop
    return {}


def exchanges_as_dataframe(dataset):
    """Return an pandas dataframe which describes the exchanges in dataset ``dataset``.

    The dataframe has the following columns:

    * ``name``: str, name of exchange flow
    * ``amount``: float, amount of exchange
    * ``type``: str, type of exchange
    * ``price``: float, amount of property named ``price``. Default is 0 if property ``price`` is not provided.
    * ``has true value``: bool, whether a property names ``true value relation`` is present in this exchange.
    * ``true value``: float, amount of property named ``true value relation``. Default is 0 if property ``true value relation`` is not provided.
    * ``revenue``: float, price * amount.

    """
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
