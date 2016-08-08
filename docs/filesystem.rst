Writing data
************

Ocelot will write a lot of data during a model run. It will also cache some data that can be used across model runs.

Base directory for saving data
==============================

Ocelot uses the `appdirs library <https://pypi.python.org/pypi/appdirs>`__ to select an appropriate, platform-specific path for saving data:

* On Windows: ``C:\Documents and Settings\<User>\Application Data\Local Settings\ocelot_project\Ocelot``
* On OS X: ``/Users/<User>/Library/Application Support/Ocelot``
* On Linux: ``/home/<User>/.local/share/Ocelot``

.. autofunction:: ocelot.filesystem.get_base_directory


Caching data extracted from ecospold2 files
===========================================

Extracting data from ecospold2 files is relatively expensive, and can take up to a few minutes. Ocelot will by cache the extracted data in order to speed up subsequent model runs. The cache directory is a subdirectory of the base directory, called ``"cache"``.

To disable the use of the cached data in a system model run, call ``system_model(..., use_cache=False)``.

Cache management functions
--------------------------

The following functions in ``ocelot.filesystem`` manage the cached data:

.. autofunction:: ocelot.filesystem.get_cache_directory

.. autofunction:: ocelot.filesystem.check_cache_directory

.. autofunction:: ocelot.filesystem.get_from_cache

.. autofunction:: ocelot.filesystem.cache_data


Model run output
================

Model runs are stored in a subdirectory of the base directory called ``"model-runs"``. However, a custom location for storing model run outputs can be specified in the environment variable ``OCELOT_OUTPUT``. The environment variable will always take precedence over the default location. See your operating system manual for instructions on setting environment variables.

.. autofunction:: ocelot.filesystem.get_output_directory
