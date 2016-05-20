Technical reference
===================

Transform functions
-------------------

Transform functions are the heart of Ocelot - each one performs one distinct change to the collection of datasets. Transform functions can be any callable, bit are mostly commonly functions.

The report generator will use information about each transform function when creating the report. Specifically, the report generator will look at the function name, its `docstring <https://www.python.org/dev/peps/pep-0257/>`__ (a text description of what the function does, included in the function code), and a new attribute ``__table__``.

If you need to initialize functions using `functools.partial <https://docs.python.org/3.5/library/functools.html#functools.partial>`__, the report generator will still get the correct function metadata. Other forms of currying are not supported.

If it is more convenient to provide logging data in tabular form in the Ocelot model run report, then define the attribute ``__table__`` as follows:

.. code-block:: python

    def foo(data):
        return data

    foo.__table__ = {
        'title': 'Name of title to put in report',
        'columns': ["names", "of", "columns"]
    }

.. _configuration:

Configuration
-------------

.. autoclass:: ocelot.Configuration

.. _systemmodel:

System model
------------

.. automethod:: ocelot.model.SystemModel

.. _report:

Report
------

.. autoclass:: ocelot.Report

.. autoclass:: ocelot.HTMLReport
