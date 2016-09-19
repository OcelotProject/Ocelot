# -*- coding: utf-8 -*-
from ...collection import Collection
from ..utils import (
    allocatable_production,
    choose_reference_product_exchange,
    get_single_reference_product,
    single_input,
)
from ..uncertainty import scale_exchange
from .economic import economic_allocation
from .validation import valid_recycling_activity, valid_waste_treatment_activity
from . import RC_STRING
from copy import deepcopy
import logging


@valid_recycling_activity
def recycling_allocation(dataset):
    """Allocate a recycling activity.

    Returns a list of new activities.

    A recycling dataset has a reference product of the material to be recycled, and a byproduct of the material that can enter a market. For example, aluminium recycling has a reference production of -1 kg of ``aluminium scrap, post-consumer, prepared for melting``, and allocatable byproducts of ``aluminium, cast alloy`` and ``aluminium oxide``.

    This function will change the reference product to an input (meaning that this activity will consume e.g. aluminium scrap), and then perform economic allocation on the byproducts.

    Note that recycling allocation is not applied to ``recyclable`` byproducts, as the cutoff system model breaks the chain between production and consumption of these types of materials.

    The net effect of ``recycling_allocation`` and ``flip_non_allocatable_byproducts`` is that all outputs that are not allocatable byproducts are moved to technosphere inputs.

    """
    rp = get_single_reference_product(dataset)
    rp['type'] = 'from technosphere'
    rp = scale_exchange(rp, -1)
    return economic_allocation(dataset)


@valid_waste_treatment_activity
def waste_treatment_allocation(dataset):
    """Perform cutoff system model allocation on a waste treatment activity.

    Returns a list of new activities.

    In the cutoff system model, the useful products of waste treatment come with no environmental burdens - they are cut off from the rest of the supply chain. So, this allocation function creates one dataset with all the environmental burdens which treats (consumes) the actual waste, and several new datasets which provide each byproduct for free.

    """
    def free_byproduct(dataset, exchange):
        """Create a new activity dataset with only one exchange"""
        new_one, byproduct = deepcopy(dataset), deepcopy(exchange)
        new_one['exchanges'] = [byproduct]
        # Label exchange as ref. product and normalize production amount
        return choose_reference_product_exchange(new_one, byproduct)

    rp = get_single_reference_product(dataset)
    return [
        choose_reference_product_exchange(dataset, rp)
    ] + [
        free_byproduct(dataset, exchange)
        for exchange in allocatable_production(dataset)
        if exchange is not rp
    ]


def rename_recyclable_content_exchanges(data):
    """Rename recyclable byproducts to indicate the cuts in their supply chain.

    Changes name of byproducts.

    The name of the recyclable flow has the following suffix added: ``, Recycled Content cut-off``, e.g. ``scrap lead acid battery, Recycled Content cut-off``."""
    found = set()
    recyclable_iterator = (exc
                           for ds in data
                           for exc in ds['exchanges']
                           if exc['type'] == 'byproduct'
                           and exc['byproduct classification'] == 'recyclable')
    for exc in recyclable_iterator:
        found.add(exc['name'])
        exc['name'] += RC_STRING
    return data


def rename_recycled_content_products_after_linking(data):
    """Change the name of recycled content products (but not activities).

    In the release version of ecoinvent, the activities have ``Recycled Content cut-off``, but the flow names don't. We can remove this suffix safely after linking."""
    exchange_iterator = (exc
                         for ds in data
                         for exc in ds['exchanges'])
    for exc in exchange_iterator:
        exc['name'] = exc['name'].replace(RC_STRING, "")
    return data


def create_new_recycled_content_dataset(ds, exc):
    """Create a new dataset that consume recycled content production."""
    common = ('access restricted', 'economic scenario', 'end date',
              'filepath', 'id', 'start date', 'technology level',
              'dataset author', 'data entry')
    obj = {
        "exchanges": [{
            'amount': 1,
            'id': exc['id'],
            'name': exc['name'],
            'tag': 'intermediateExchange',
            'type': 'reference product',
            'production volume': {'amount': 4},  # Bo's magic number
            'unit': exc['unit'],
        }],
        "parameters": [],
        'name': exc['name'],
        'location': 'GLO',
        'type': "transforming activity",
        'reference product': exc['name']
    }
    obj.update({key: ds[key] for key in common})
    return deepcopy(obj)


def create_recycled_content_datasets(data):
    """Create new datasets that consume the recyclable content from recycling or waste treatment activities in the cutoff system model.

    In the cutoff system model, no credit is given for the production of recyclable materials. Rather, consumers get these materials with no environmental burdens. So the production of a recyclable material (i.e. a flow with the classification ``recyclable``) during any transforming activity will create a new flow which has no consumer. This function creates consuming activities for these flows. These new activities have no environmental burdens, and serve no purpose other than to balance the output of a recyclable material."""
    new_datasets = {}
    for ds in data:
        recyclables = (exc
                       for exc in ds['exchanges']
                       if exc['type'] == 'byproduct'
                       and exc['byproduct classification'] == 'recyclable')
        for exc in recyclables:
            rc = create_new_recycled_content_dataset(ds, exc)
            new_datasets[rc['name']] = rc
    for name in new_datasets:
        logging.info({
            'type': 'table element',
            'data': (name,),
        })
    return data + list(new_datasets.values())

create_recycled_content_datasets.__table__ = {
    'title': 'Create new datasets to consume recyclable byproducts',
    'columns': ["Activity name"]
}


@single_input
def flip_non_allocatable_byproducts(dataset):
    """Change non-allocatable byproducts (i.e. classification ``recyclable`` or ``waste``) from outputs to technosphere to inputs from technosphere.

    This has no effect on the technosphere matrix, and should not change the behaviour of any transformation functions, which should be testing for classification instead of exchange type. However, this is the current behaviour of the existing ecoinvent system model.

    Production of recyclable materials are handled by the function ``create_recycled_content_datasets``, which creates consuming activities for these materials. Production of wastes will be handled by existing waste treatment activities.

    Change something from an output to an input requires flipping the sign of all numeric fields.

    """
    for exc in dataset['exchanges']:
        if (exc['type'] == 'byproduct' and
                exc['byproduct classification'] != 'allocatable product'):
            logging.info({
                'type': 'table element',
                'data': (dataset['name'], exc['name'], exc['byproduct classification']),
            })
            del exc['byproduct classification']
            exc['type'] = 'from technosphere'
            # TODO: Use rescale_exchange when new uncertainties code is merged
            exc['amount'] = -1 * exc['amount']
            if 'formula' in exc:
                exc['formula'] = '-1 * ({})'.format(exc['formula'])
    return [dataset]

flip_non_allocatable_byproducts.__table__ = {
    'title': 'Flip recyclable and waste outputs to inputs for cutoff or treatment',
    'columns': ["Activity name", "Flow", "Classification"]
}


handle_waste_outputs = Collection(
    rename_recyclable_content_exchanges,
    create_recycled_content_datasets,
    flip_non_allocatable_byproducts,
)
