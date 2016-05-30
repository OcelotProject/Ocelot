Internal data formats
*********************

Datasets
========

Internally, datasets have the bare minimum of information needed for successful linking. Most information from `ecospold2 files <http://www.ecoinvent.org/data-provider/data-provider-toolkit/ecospold2/ecospold2.html>`__ is not read, as it is not needed during Ocelot runs and would needlessly consume resources to manage.

Here is the Python data format for a single dataset:

.. code-block:: python

    {
        'name': str,
        'filepath': str,
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
            # XML tag name for this exchange;
            # either 'intermediateExchange' or 'elementaryExchange'
            'tag': str,
            'type': str,
            'unit': str
        }],
        # Starting and ending dates for dataset validity, in format '2015-12-31'
        'temporal': (str, str),
        'type': str,
    }

Multioutput datasets may also have the following fields:

.. code-block:: python

    {
        'parameters': [{
            'amount': float,
            'name': str,
            'variable': str,
            'formula': str,
            'uncertainty': [{
                # Optional, and filled with distribution-specific numeric fields,
                # e.g. 'mean', 'maximum', 'minimum', as well as the following:
                'pedigree matrix': tuple of integers,
                'type': str,
            }]
        }],
        'exchanges': [{  # In addition to normal exchange fields
            'formula': str,
            'variable': str,
            'properties': [{
                'amount': float,
                'id': str,
                'name': str,
                'variable': str,
                'formula': str,
                'uncertainty': [{
                    # Optional, and filled with distribution-specific numeric fields,
                    # e.g. 'mean', 'maximum', 'minimum', as well as the following:
                    'pedigree matrix': tuple of integers,
                    'type': str,
                }]
            }]
        }],
    }

.. _logging-format:

Logging format
==============

The :ref:`logger` class will generate the following types messages. Each message is JSON-encoded, and on a separate line.

Report start
------------

.. code-block:: javascript

    {
        type: 'report start',
        time: time at report start, UNIX timestamp,
        count: int, number of raw datasets,
        uuid: UUID of current report, hex-encoded
    }

Report end
----------

.. code-block:: javascript

    {
        type: 'report end',
        time: time at report end, UNIX timestamp
    }

Function start
--------------

.. code-block:: javascript

    {
        type: 'function start',
        time: time at function start, UNIX timestamp,
        count: current number of datasets,
        index: int, function index,
        name: name of function,
        description: description of function from function docstring,
        table: list of columns to be formatted into a table, or null
    }

Function end
------------

.. code-block:: javascript

    {
        type: 'report end',
        time: time at function end, UNIX timestamp,
        count: current number of datasets,
        index: int, function index,
        name: name of function,
        description: description of function from function docstring,
        table: list of columns to be formatted into a table, or null
    }

Function data
-------------

Function will also write log messages about individual changes. These messages have no particular format, but if they are providing data which will be formatted into a table later, they will look like:

.. code-block:: javascript

    {
        type: 'table element',
        data: list of data elements in same order as columns
    }
