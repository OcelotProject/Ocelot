.. _writing:

Writing your own transformation functions
*****************************************

A transformation function takes the current list of datasets as an input, does some transformation to these datasets, and then returns the changed data. For example, here is a transformation function that doubles the amount of each exchange:

.. code-block:: python

    def doubler(data):
        for ds in data:
            for exc in ds['exchanges']:
                exc['amount'] *= 2
        return data

To make reporting meaningful, transformation functions should follow several conventions, explained in the the following sections.

Input arguments: all data or a single dataset
=============================================

This choice is entirely up to you. Both types of input arguments are used in the Ocelot codebase, and some functions seem to fit more naturally into one input type or the other.

In general, if your function takes all data as its input, this argument should be called ``data``. If your function takes a single dataset, then the argument should be labeled ``dataset``. This is not a hard rule, and is not enforced, but will make it easier for others to understand your code.

The `single_input` decorator
----------------------------

If you are writing a transformation function that takes a single dataset as its input, wrap it with the ``single_input`` decorator:

.. code-block:: python

    from ocelot.transformations.utils import single_input

    @single_input
    def doubler_variation(dataset):
        for exc in dataset['exchanges']:
            exc['amount'] *= 2
    return [dataset]  # Note that this is a list

If you use the ``single_input`` decorator, be aware of the following rules:

* The input will be a single dataset
* The function should return a list of datasets, as transformation functions can split datasets

Logging what your function does
===============================

Report logging
--------------

Report logging is data which will go into the HTML report which is produced at the end of each Ocelot model run. Most of the time you will want to provide logging data that will be turned into tables in this report. To tell the report generator how to define these tables, define the function attribute ``__table__`` as follows:

.. code-block:: python

    def some_transformation(data):
        return data

    some_transformation.__table__ = {
        'title': 'Name of title to put in report',
        'columns': ["names", "of", "columns"]
    }

``__table__`` should define:

    * ``title``: The title of the function data provided
    * ``columns``: A list of column headings

There should also be logging inside the transformation function. You need to retrieve the ``ocelot`` logger, and log using the log level ``info``. So, a more complete example would actually look something like this:

.. code-block:: python

    logger = logging.getLogger('ocelot')  # Very important

    def count_exchanges(data):
        """Function that counts things.

        Does not change any data."""
        for ds in data:
            logger.info({
                'type': 'table element',
                'data': [ds['name'], len(ds['exchanges'])]
            })
        return data

    count_exchanges.__table__ = {
        'title': 'Count the number of exchanges in each dataset',
        'columns': ["Name", "# of exchanges"]
    }

Log messages should be a dictionary, with the key ``type`` (and value ``table element`` for tabular data). The key ``data`` should give a list of data in the same order as ``columns``.

If tables don't work for your transformation function, you can skip the ``__table__`` attribute, and just log ``list element`` log messages:

.. code-block:: python

    logger = logging.getLogger('ocelot')

    def count_exchanges(data):
        """Function that counts things.

        Does not change any data."""
        for ds in data:
            logger.info({
                'type': 'list element',
                'data': "Dataset <b>{}</b> has <i>{}</i> exchanges".format(
                    ds['name'], len(ds['exchanges'])
                )
            })
        return data

Messages that have the type ``list element`` can be HTML.

Detailed logging
----------------

Transformation functions should also write detailed logs that can be used afterwards to debug exactly what happened to a dataset. This logging uses a different data format and logger.

First, retrieve the detailed logger:

.. code-block:: python

    detailed = logging.getLogger('ocelot-detailed')

Then, inside the body of a function, call this logger (again using the ``info`` log level):

.. code-block:: python

    def count_exchanges(data):
        """Function that counts things.

        Does not change any data."""
        for ds in data:
            detailed.info({
                'ds': ds,
                'message': 'Some message about number of exchanges',
                'function': 'count_exchanges'
            })
        return data

In the detailed log messages, the following keys are required:

    * ``ds``: The dataset object being changed. If you don't have access or can't provide this dataset, don't emit a detailed log message.
    * ``function``: The name of the function (as a string)
    * ``message``: The message to log (as a string)

Currying transformation functions
=================================

If you need to initialize functions using `functools.partial <https://docs.python.org/3.5/library/functools.html#functools.partial>`__, the report generator will still get the correct function metadata. Other forms of currying are not supported.
