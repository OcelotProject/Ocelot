# -*- coding: utf-8 -*-
from ...errors import InvalidMultioutputDataset


def choose_allocation_method(dataset):
    """Choose from among the following allocation methods:

    * combined production with byproducts
    * combined production without byproducts
    * constrained market
    * economic
    * recycling
    * true value
    * waste treatment

    TODO: Do we need to check for non-zero amounts for all exchanges use for flags below?

    TODO: It feels strange to get reference product classification from the byproduct classification... this should at least be described a bit.

    The chosen method is returned as a string. Can also return ``None``.

    """
    reference_product_classifications = [exc['byproduct classification']
                                         for exc in dataset['exchanges']
                                         if exc['type'] == 'reference product'
                                         and exc['amount'] != 0]
    number_reference_products = len(reference_product_classifications)
    negative_reference_production = any(1 for exc in dataset['exchanges']
                                        if exc['type'] == 'reference product'
                                        and exc['amount'] < 0)
    allocatable_byproducts = any(1 for exc in dataset['exchanges']
                                 if exc['type'] == 'byproduct'
                                 and exc['byproduct classification'] == 'allocatable'
                                 and exc['amount'] != 0)
    true_value = any(1 for exc in dataset['exchanges']
                     for prop in exc.get('properties', {})
                     if exc['amount'] != 0
                     and prop.get('name') == 'true value relation')
    has_conditional_exchange = any(1 for exc in dataset['exchanges']
                                   if exc['type'] == 'byproduct'
                                   and exc['amount'] != 0
                                   and exc.get('conditional exchange'))

    # Validity checks
    if dataset['type'] == 'market group':
        assert number_reference_products == 1
        assert not allocatable_byproducts

    # No allocation needed
    if dataset['type'] == 'market group':
        return None
    elif number_reference_products == 1 and not allocatable_byproducts:
        return None
    elif dataset['type'] == 'market activity' and not has_conditional_exchange:
        # TODO: Why is there no allocation here? Still have more than one
        # reference product, or some byproducts?
        return None

    # Choose between available methods
    if dataset['type'] == 'market activity' and has_conditional_exchange:
        return 'constrained market'
    elif number_reference_products > 1:
        if allocatable_byproducts:
            return 'combined production with byproducts'
        else:
            return 'combined production without byproducts'
    elif negative_reference_production:
        assert len(set(reference_product_classifications)) == 1
        if reference_product_classifications[0] == 'waste':
            return 'waste treatment'
        else:
            return "recycling"
    else:
        return "true value" if true_value else 'economic allocation'
