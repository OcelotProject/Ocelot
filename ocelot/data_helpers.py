# -*- coding: utf-8 -*-


def production_volume(dataset):
    """Get production volume of reference product exchange.

    Returns ``None`` if no or multiple reference products, or if reference product doesn't have a production volume amount."""
    exchanges = [x for x in dataset['exchanges']
                 if x['type'] == 'reference product']
    if len(exchanges) != 1:
        return None
    else:
        try:
            return exchanges[0]['production volume']['amount']
        except KeyError:
            return None


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
