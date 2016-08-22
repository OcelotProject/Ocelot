# -*- coding: utf-8 -*-
from .utils import allocatable_production
from ..errors import (
    InvalidMarket,
    InvalidMarketExchange,
    InvalidMultioutputDataset,
    MissingMandatoryProperty,
)


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
    """"Markets are only allowed to have one reference product exchange.

    Raises ``InvalidMarket`` if multiple outputs were found."""
    for ds in (obj for obj in data if obj['type'] == 'market activity'):
        if sum(1 for exc in ds['exchanges'] if exc['type'] == 'reference product') != 1:
            message = "Market dataset has zero or multiple reference products:\{}"
            raise InvalidMarket(message.format(ds['filepath']))
    return data


def ensure_markets_dont_consume_their_ref_product(data):
    """Markets aren't allowed to consumer their own reference product.

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


def ensure_mandatory_properties(data):
    """If an exchange has properties, it must include the mandatory properties.

    dry mass, water in wet mass, water content, wet mass, carbon content fossil, and carbon content non fossil."""
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
                    message = "Exchange is missing mandatory properties: {}\n{}"
                    raise MissingMandatoryProperty(message.format(missing, ds['filepath']))
    return data

