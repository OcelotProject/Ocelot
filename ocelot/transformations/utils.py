# -*- coding: utf-8 -*-
from ..errors import InvalidMultioutputDataset, ZeroProduction
from ..uncertainty import scale_exchange
from pprint import pformat
import hashlib
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


def nonproduction_exchanges(dataset):
    """Return generator of non-production exchanges for a dataset.

    Non-production exchanges must meet both criteria:

    * Not have type ``reference product``, or
    * Not have type ``byproduct`` and ``byproduct classification`` ``allocatable``

    """
    for exc in dataset['exchanges']:
        if exc['type'] =='reference product':
            continue
        elif (exc['type'] == 'byproduct' and
              exc['byproduct classification'] == 'allocatable'):
            continue
        yield exc


def extract_products_as_tuple(dataset):
    """Return names of all products as a sorted tuple.

    Products are chosen using ``allocatable_production``."""
    return tuple(sorted([exc['name'] for exc in allocatable_production(dataset)]))


def activity_grouper(dataset):
    """Return tuple of dataset name and products.

    Products are chosen using ``extract_products_as_tuple``."""
    return (dataset['name'], extract_products_as_tuple(dataset))


def get_property_by_name(exchange, name):
    """Get property object with name ``name`` from exchange ``exchange``.

    Returns an empty dictionary if the property named ``name`` is not found."""
    for prop in exchange.get("properties", []):
        if prop['name'] == name:
            return prop
    return {}


def get_numerical_property(exchange, name):
    """Get ``amount`` value for property ``property_name`` in exchange ``exchange``.

    Returns a float or ``None``."""
    return get_property_by_name(exchange, name).get('amount')


def allocatable_production_as_dataframe(dataset):
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


def get_single_reference_product(dataset):
    """Return reference product exchange for dataset ``dataset``.

    Raises ``InvalidMultioutputDataset`` if multiple reference products were found, ``ValueError`` if no reference product was found."""
    products = [exc for exc in dataset['exchanges']
                if exc['type'] == 'reference product']
    if len(products) > 1:
        message = "Found multiple reference products in dataset:\n{}"
        raise InvalidMultioutputDataset(message.format(pformat(dataset)))
    elif not products:
        message = "Found no reference products in dataset:\n{}"
        raise ValueError(message.format(pformat(dataset)))
    return products[0]


def normalize_reference_production_amount(dataset):
    """Scale the exchange amounts so the reference product exchange has an amount of 1 or -1"""
    product = get_single_reference_product(dataset)
    if not product['amount']:
        message = "Zero production amount for dataset:\n{}"
        raise ZeroProduction(message.format(pformat(dataset)))
    factor = 1 / abs(product['amount'])
    # TODO: Skip if very close to one?
    if factor != 1:
        for exchange in dataset['exchanges']:
            scale_exchange(exchange, factor)
    return dataset


def activity_hash(dataset):
    """Return the hash string that uniquely identifies an activity.

    Uses the following fields, in order:
        * name
        * reference product
        * unit
        * location
        * start date
        * end date

    An empty string is used if a field isn't present. All fields are cast to lower case.

    """
    fields = (
        "name",
        "reference product",
        "unit",
        "location",
        "start date",
        "end date",
    )
    string = "".join(dataset.get(field, '').lower() for field in fields)
    return hashlib.md5(string.encode('utf-8')).hexdigest()


def label_reference_product(dataset):
    """Set ``reference product`` key for ``dataset``.

    Uses ``get_single_reference_product``."""
    dataset['reference product'] = get_single_reference_product(dataset)['name']
    return dataset
