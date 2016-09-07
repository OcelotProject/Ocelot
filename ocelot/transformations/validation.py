# -*- coding: utf-8 -*-
from .utils import allocatable_production
from ..collection import Collection
from ..errors import (
    IdenticalDatasets,
    InvalidExchange,
    InvalidMarket,
    InvalidMarketExchange,
    InvalidMultioutputDataset,
    # MissingMandatoryProperty,
)
from pprint import pformat
import logging


def ensure_ids_are_unique(data):
    """Make sure that ids are actually unique"""
    if len({ds['id'] for ds in data}) != len(data):
        raise IdenticalDatasets
    return data


def check_single_output_activity(dataset):
    """Check that the activity has exactly one reference product and no allocatable byproducts.

    Raise ``InvalidMultioutputDataset`` if any of these conditions are not met."""
    num_rp = sum(1 for exc in dataset['exchanges']
                 if exc['type'] == 'reference product')
    byproducts = any(1 for exc in dataset['exchanges']
                     if exc['type'] == 'byproduct'
                     and exc['byproduct classification'] == 'allocatable product')
    if num_rp != 1:
        raise InvalidMultioutputDataset("Found {} reference products".format(num_rp))
    if byproducts:
        raise InvalidMultioutputDataset("Found allocatable byproducts")
    return dataset


def ensure_markets_only_have_one_reference_product(data):
    """Markets are only allowed to have one reference product exchange.

    Raises ``InvalidMarket`` if zero or multiple outputs were found."""
    for ds in (obj for obj in data if obj['type'] == 'market activity'):
        if sum(1 for exc in ds['exchanges'] if exc['type'] == 'reference product') != 1:
            message = "Market dataset has zero or multiple reference products:\{}"
            raise InvalidMarket(message.format(ds['filepath']))
    return data


def ensure_markets_dont_consume_their_ref_product(data):
    """Markets aren't allowed to consume their own reference product.

    Raise ``InvalidMarketExchange`` if such an exchange is found.

    Direct (activity) links are excepted from this rule."""
    for ds in (obj for obj in data if obj['type'] == 'market activity'):
        rp = [exc for exc in ds['exchanges'] if exc['type'] == 'reference product'][0]
        if any(exc for exc in ds['exchanges']
               if exc['name'] == rp['name']
               and exc != rp
               and not exc.get("activity link")):
            message = "Market dataset has exchanges which consume the ref. product:\n{}"
            raise InvalidMarketExchange(message.format(ds['filepath']))
    return data


validate_markets = Collection(
    ensure_markets_only_have_one_reference_product,
    ensure_markets_dont_consume_their_ref_product,
)


def ensure_mandatory_properties(data):
    """If an exchange has properties, it should include the mandatory properties.

    * dry mass
    * water in wet mass
    * water content
    * wet mass
    * carbon content fossil
    * carbon content non fossil

    This function logs exchanges which are missing some of these mandatory properties."""
    MANDATORY = {"dry mass", "water in wet mass", "water content", "wet mass", "carbon content fossil", "carbon content non-fossil"}

    for ds in data:
        for exc in ds['exchanges']:
            if exc.get("properties"):
                for prop in exc['properties']:
                    if prop['name'] in MANDATORY:
                        if 'amount' not in prop:
                            raise ValueError
                missing = MANDATORY.difference({p['name'] for p in exc['properties']})
                if missing:
                    logging.info({
                        'type': 'table element',
                        'data': (ds['name'], exc['name'], "; ".join(sorted(missing)))
                    })
                    # message = "Exchange is missing mandatory properties: {}\n{}"
                    # raise MissingMandatoryProperty(message.format(missing, ds['filepath']))
    return data

ensure_mandatory_properties.__table__ = {
    'title': 'Exchanges with properties should have all mandatory properties',
    'columns': ["Activity name", "Flow name", "Missing properties"]
}


def ensure_production_exchanges_have_production_volume(data):
    """All production exchanges must have a ``production volume``."""
    for ds in data:
        for exc in allocatable_production(ds):
            if 'production volume' not in exc:
                message = "No production volume in production exchange:\n{}\nIn dataset: {}"
                raise InvalidExchange(message.format(pformat(exc), ds['filepath']))
    return data
