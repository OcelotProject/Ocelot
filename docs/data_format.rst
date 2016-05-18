Internal data format specification
==================================

Internally, datasets have the bare minimum of information needed for successful linking. Most information from `ecospold2 files <http://www.ecoinvent.org/data-provider/data-provider-toolkit/ecospold2/ecospold2.html>`__ is not read, as it is not needed and would needlessly consume resources to manage.

Here is the data format for a single dataset:

.. code-block:: python

    {
        'name': str,
        'location': str,
        'technology level': str,
        'economic': str,
        'exchanges': [{
            'amount': float,
            'id': uuid as hex-encoded string,
            'name': str,
            # The following only applies to exchanges whose "type" is "reference product"
            'production volume': {
                'amount': float,
                # Optional name of this numeric value as a variable
                'variable': str,
                # Optional formula defining this numeric value
                'formula': str,
                'uncertainty': {
                    # Optional, and filled with distribution-specific numeric fields,
                    # e.g. 'mean', 'maximum', 'minimum', as well as the following:
                    'pedigree matrix': tuple of integers,
                    'type': str,
                }
            },
            # XML tag name for this exchange
            'tag': str,
            'type': str,
            'unit': str
        }],
        # Starting and ending dates for dataset validity, in format '2015-12-31'
        'temporal': (str, str),
        'type': str,
    }
