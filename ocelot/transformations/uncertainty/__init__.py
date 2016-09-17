# -*- coding: utf-8 -*-


def remove_exchange_uncertainty(exchange):
    """Remove uncertainty from the given ``exchange``"""
    if 'uncertainty' in exchange:
        del exchange['uncertainty']
    return exchange


from ...errors import UnsupportedDistribution
from .distributions import (
    Lognormal,
    Normal,
    NoUncertainty,
    Triangular,
    Undefined,
    Uniform,
)
from .pedigree import get_pedigree_variance, adjust_pedigree_matrix_time as apmt

TYPE_MAPPING = {
    'lognormal': Lognormal,
    'normal': Normal,
    'triangular': Triangular,
    'undefined': Undefined,
    'uniform': Uniform,
    None: NoUncertainty,
}


def get_uncertainty_class(exchange):
    try:
        return TYPE_MAPPING[exchange.get('uncertainty', {}).get('type')]
    except KeyError:
        raise UnsupportedDistribution


def scale_exchange(exchange, factor):
    """Scale an ``exchange`` and its uncertainty by a constant numeric ``factor``.

    Modifies the exchange in place. Returns the modified exchange."""
    if factor == 1:
        return exchange
    return get_uncertainty_class(exchange).rescale(exchange, factor)


def adjust_pedigree_matrix_time(ds, exchange, year):
    exchange = apmt(ds, exchange, year)
    return get_uncertainty_class(exchange).recalculate(exchange)
