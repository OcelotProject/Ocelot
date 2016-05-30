Running Ocelot
==============

Installation of Ocelot will install a command line utility, ``ocelot-cli``. This utility supports the following modes:

Ocelot system model run
-----------------------

The main way to run the utility using the default system model is:

.. code-block:: bash

    ocelot-cli run /path/to/ecospold2/data/directory

On Windows, the path would be something like:

.. code-block:: bash

    ocelot-cli run C:\\path\\to\\ecospold2\\directory

Note that the backslashes (``\``) should be doubled.

If you want to specify a custom system model configuration, you can give its path as the second argument:

.. code-block:: bash

    ocelot-cli run /path/to/ecospold2/data/directory /path/to/config/file

.. note:: Custom configurations are not yet usable in the current code!

By default, Ocelot will open the generated HTML report in a new browser tab. To disable this behaviour, add the option ``--noshow``:

.. code-block:: bash

    ocelot-cli run /path/to/ecospold2/data/directory --noshow

Cleanup old model runs
----------------------

To delete all run outputs older than one week, run:

.. code-block:: bash

    ocelot-cli cleanup

Validate input ecospold2 files
------------------------------

Ocelot can also validate your ecospold2 files against the ecospold2 1.0.3 specification:

.. code-block:: bash

    ocelot-cli validate /path/to/ecospold2/data/directory

Miscellaneous
-------------

* ``ocelot-cli --help``: Print some basic usage help
* ``ocelot-cli --list``: List these usage options
* ``ocelot-cli --version``: Print the command line utility version number

