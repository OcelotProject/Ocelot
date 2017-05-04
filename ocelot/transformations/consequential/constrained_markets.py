# -*- coding: utf-8 -*-
from ... import toolz
from ..utils import get_single_reference_product
import logging


def flip_exchange(exc):
    """Flip amount and formula of an exchange"""
    exc['amount'] = -1 * exc['amount']
    if 'formula' in exc:
        exc['formula'] = '-1 * ({})'.format(exc['formula'])
    return exc


def handle_constrained_markets(data):
    """Handle constrained markets and their activity links to transforming activities.

    We follow the `ecoinvent description <http://www.ecoinvent.org/support/faqs/methodology-of-ecoinvent-3/what-is-a-constrained-market-how-is-it-different-from-the-normal-market-how-does-it-behave-during-the-linking.html>`__ of constrained markets.

    A constrained exchange has the following attributes:

    * They only occur in market activities
    * They have a negative amount
    * They have the type ``byproduct``
    * They have an activity link
    * They have a property ``consequential`` with a value of 1

    This can be conceptually difficult, because we need to understand the full algorithm to see how changes in exchange types propagate to the linking algorithm, which ends up leading to changes in the technosphere matrix.

    We need to do the following:

    * Move the activity link constrained exchange from a byproduct to an input (and multiply amount by -1)
    * In the linked transforming activity, move the previous reference product to an input (and multiply amount by -1)
    * In the linked transforming activity, move the input with the same product name as the constrained exchange to a reference product (and multiply amount by -1)

    """
    id_mapping = {ds['id']: ds for ds in data}
    for ds in data:
        for exc in (e for e in ds['exchanges'] if e.get('conditional exchange')):
            # Activity link validity is check by separate validation function
            target = id_mapping[exc['activity link']]

            # Handle exchange in this dataset
            exc['type'] = 'from technosphere'
            flip_exchange(exc)

            # Find and modify current target reference product
            target_rp = get_single_reference_product(target)
            target_rp['type'] = 'from technosphere'
            flip_exchange(target_rp)

            # Find and modify corresponding exchange in target
            target_excs = [e for e in target['exchanges'] if e['name'] == exc['name']]
            assert len(target_excs) == 1, "Can't find corresponding input"
            target_exc = target_excs[0]
            assert target_exc['type'] == 'from technosphere', "Wrong type for activity link target"
            target_exc['type'] = 'reference product'
            target_exc['byproduct classification'] = 'allocatable product'
            flip_exchange(target_exc)

            logging.info({
                'type': 'table element',
                'data': (exc['name'], target['name'],
                         target['location'], target_rp['name']),
            })
    return data

handle_constrained_markets.__table__ = {
    'title': 'Handle constrained markets and their activity links to transforming activities.',
    'columns': ["Flow", "Target name", "Target location", "Replaced flow"]
}


def delete_activity_links_to_constrained_markets(data):
    """Activity links to constrained markets can't be fulfilled, so they are deleted.

    See example of global production of "ethoxylated alcohol (AE3) production, palm kernel oil". In the undefined dataset, there is an input of fatty alcohol with an activity link to global production of "fatty alcohol production, from palm kernel oil". However, in the consequential release files this link is changed to an activity link to "market for fatty alcohol". As this is the normal linking result for an input of fatty alcohol, we don't change the activity link, but just delete it.

    Dataset links:

    * `ethoxylated alcohol (AE3) production, palm kernel oil, undefined <https://v32.ecoquery.ecoinvent.org/Details/UPR/aa84b502-1db8-45f9-8b22-df2fe8ce71d6/8b738ea0-f89e-4627-8679-433616064e82>`__
    * `ethoxylated alcohol (AE3) production, palm kernel oil, consequential <https://v32.ecoquery.ecoinvent.org/Details/UPR/7c0c4f2e-41c6-408e-ad5f-a3070337503f/dd7f13f5-0658-489c-a19c-f2ff8a00bdd9>`__

    """
    constrained_activities = {
        exc['activity link']
        for ds in data
        for exc in ds['exchanges']
        if exc.get('conditional exchange')
    }
    for ds in data:
        exchange_iterator = (
            exc for exc in ds['exchanges']
            if not exc.get('conditional exchange')
            and exc.get('activity link')
        )
        for exc in exchange_iterator:
            del exc['activity link']
            logging.info({
                'type': 'table element',
                'data': (ds['name'], ds['location'],
                         exc['name'], exc['amount']),
            })
    return data

delete_activity_links_to_constrained_markets.__table__ = {
    'title': '',
    'columns': ["Activity", "Location", "Flow", "Amount"]
}
