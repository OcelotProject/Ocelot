Running Ocelot
--------------

Installation of Ocelot will install a command line utility, ``ocelot-cli``. Run ``ocelot-cli -h`` to see all options. The main way to run the utility using the default system model is:

.. code-block:: bash

    ocelot-cli run /path/to/ecospold2/data/directory

Alternatively, if you want to specify a custom configuration:

.. code-block:: bash

    ocelot-cli run /path/to/ecospold2/data/directory /path/to/config/file

.. note:: Custom configurations are not yet usable in the current code!
