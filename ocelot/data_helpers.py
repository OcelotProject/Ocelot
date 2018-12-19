# -*- coding: utf-8 -*-


def production_volume(dataset, default=None):
    """Get production volume of reference product exchange.

    Returns ``default`` (default value is ``None``) if no or multiple
    reference products, or if reference product doesn't have a production
    volume amount."""
    exchanges = [x for x in dataset['exchanges']
                 if x['type'] == 'reference product']
    if len(exchanges) != 1:
        return default
    else:
        try:
            return exchanges[0]['production volume']['amount']
        except KeyError:
            return default


def original_production_volume(dataset, default=None):
    """Get original (i.e. before activity link subtractions) production volume of reference product exchange.

    Returns ``default`` (default value is ``None``) if no or multiple
    reference products, or if reference product doesn't have a production
    volume amount."""
    exchanges = [x for x in dataset['exchanges']
                 if x['type'] == 'reference product']
    if len(exchanges) != 1:
        return default
    try:
        pv = exchanges[0]['production volume']
    except KeyError:
        return default
    if 'original amount' in pv:
        return pv['original amount']
    elif 'amount' in pv:
        return pv['amount']
    else:
        return default


def reference_products_as_string(dataset):
    """Get all reference products as a string separated by ``'|'``.

    Return ``'None found'`` if no reference products were found."""
    exchanges = sorted([exc['name']
                        for exc in dataset['exchanges']
                        if exc['type'] == 'reference product'])
    if not exchanges:
        return "None found"
    else:
        return "|".join(exchanges)
