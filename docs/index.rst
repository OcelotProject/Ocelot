.. image:: images/ocelot-logo.png
    :align: center

Ocelot
======

The Ocelot project is a joint effort by the Paul Scherrer Institut and the ecoinvent centre to build an open source library for applying system models in life cycle assessment. See more information at https://ocelot.space/; the source code is `on Github <https://github.com/OcelotProject/Ocelot>`__.

.. warning:: Ocelot is under heavy development, and does not yet produce a complete database.

Installation notes
------------------

Ocelot is designed for Python 3.4 or higher.

Command line
------------

Installation of Ocelot will install a command line utility, ``ocelot-cli``. Run ``ocelot-cli -h`` to see all options. The main way to run the utility using the default system model is:

.. code-block:: bash

    ocelot-cli run /path/to/ecospold2/data/directory

Alternatively, if you want to specify a custom configuration:

.. code-block:: bash

    ocelot-cli run /path/to/ecospold2/data/directory /path/to/config/file

.. note:: Custom configurations are not yet usable in the current code!

Tests
-----

Run tests with `py.test <http://pytest.org/latest/>`__ using the command ``py.test`` in the source directory. Requires a source checkout.

Manual
======

Contents:

.. toctree::
   :maxdepth: 2

   data_format
   technical

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

