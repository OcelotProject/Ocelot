# -*- coding: utf-8 -*-
import numpy as np
from .utils import (
    production_exchanges,
    get_numerical_property,
)


def true_value_allocation(dataset):
    """Perform true value allocation on a dataset.

    Returns a numpy array of allocation factors with shape (number of new datasets, number of exchanges).

    The idea of 'true value allocation' is that prices are sometimes stupid, or, in the language of the `data quality guidelines <http://www.ecoinvent.org/files/dataqualityguideline_ecoinvent_3_20130506.pdf>`__, "prices may be influenced by market imperfections or regulation that distorts markets, resulting in relative prices that have very little to do with the true, functional value of the products." (p. 131).

    So, for exchanges that have the property ``true value relation``, we use this instead of the price. However, not all outputs will have this property, and we only want to change the weight of the exchanges which have ``true value relation`` **relative to each other** - so the formula gets a bit tricky. In the following, :math:`i` is an individual exchange and :math:`j` is the set of all exchanges, :math:`i \in j`. :math:`t` is the set of all exchanges which have ``true value relation``, and :math:`n` is the set of exchanges which don't, :math:`t \cup n = j`.

    .. math::

        revenue_{i} = price_{i} * amount_{i}

        true\_value_{i \in t} = true\_value\_relation_{i} * amount_{i}

        true\_value\_scaling = \\frac{\sum_{t} revenue}{\sum_{t} true\_value}

    The allocation factor :math:`\\theta` for an exchange with has ``true value relation`` would be:

    .. math::

        \\theta_{i \in t} = \\frac{true\_value_{i}}{\sum_{t} true\_value} true\_value\_scaling

    And the allocation factor :math:`\\theta` for exchange without ``true value relation`` would be:

    .. math::

        \\theta_{i \in n} = \\frac{revenue_{i}}{\sum_{n} revenue}

    """
    factors = np.zeros((
        len(production_exchanges(dataset)),
        len(dataset['exchanges'])
    ))
    revenue = np.array([
        get_numerical_property(exc, 'price') or 0 * exc['amount']
        for exc in dataset['exchanges']
    ])
    true_values = np.array([
        get_numerical_property(exc, 'true value relation') or 0 * exc['amount']
        for exc in dataset['exchanges']
    ])
