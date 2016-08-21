# -*- coding: utf-8 -*-
import numpy as np
from .utils import apply_allocation_factors
from .validation import valid_economic_activity
from ..utils import (
    allocatable_production,
    get_numerical_property,
    allocatable_production_as_dataframe,
)


@valid_economic_activity
def economic_allocation(dataset, use_true_value=True):
    """Perform economic allocation on a dataset.

    Wrapped by ``needs_allocation``, this function returns a list of datasets.

    Economic allocation uses revenue (price times the amount of the exchange) to calculate the allocation factors.

    However, sometimes prices are silly, or, in the language of the `data quality guidelines <http://www.ecoinvent.org/files/dataqualityguideline_ecoinvent_3_20130506.pdf>`__, "prices may be influenced by market imperfections or regulation that distorts markets, resulting in relative prices that have very little to do with the true, functional value of the products" (p. 131). In this case `true value allocation` is performed.

    True value allocation is always used when an exchange has the property ``true value relation``. However, not all outputs will have this property, and we only want to change the weight of the exchanges which have ``true value relation`` **relative to other true value exchanges** - so the formula gets a bit tricky. In the following, :math:`i` is an individual exchange and :math:`j` is the set of all exchanges, :math:`i \in j`. :math:`t` is the set of all exchanges which have ``true value relation``, and :math:`n` is the set of exchanges which don't, :math:`t \cup n = j`.

    .. math::

        revenue_{i} = price_{i} * amount_{i}

        true\_value_{i \in t} = true\_value\_relation_{i} * amount_{i}

    The allocation factor :math:`\\theta` for an exchange with has ``true value relation`` would be:

    .. math::

        \\theta_{i \in t} = \\frac{true\_value_{i}}{\sum_{t} true\_value} \\frac{\sum_{t} revenue}{\sum_{j} revenue}

    And the allocation factor :math:`\\theta` for exchange without ``true value relation`` would be:

    .. math::

        \\theta_{i \in n} = \\frac{revenue_{i}}{\sum_{j} revenue}

    """
    df = allocatable_production_as_dataframe(dataset)
    factors = df['revenue'] / df['revenue'].sum()
    if use_true_value:
        mask = df['has true value']
        true_value = (df['true value'] * df['amount'])
        true_value_revenue_fraction = (
            df['revenue'][mask].sum() /
            df['revenue'].sum()
        )
        true_value = true_value / true_value.sum() * true_value_revenue_fraction
        factors[mask] = true_value[mask]
    return apply_allocation_factors(
        dataset,
        zip(factors.tolist(), allocatable_production(dataset))
    )
