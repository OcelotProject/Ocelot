.. _dataformat:

Internal data format
********************

Datasets
========

Internally, datasets have the bare minimum of information needed for successful linking. Most information from `ecospold2 files <http://www.ecoinvent.org/data-provider/data-provider-toolkit/ecospold2/ecospold2.html>`__ is not read, as it is not needed during Ocelot runs and would needlessly consume resources to manage.

Ocelot uses the `voluptuous validation library <https://pypi.python.org/pypi/voluptuous>`__ to make sure extracted datasets are formatted the way that Ocelot expects. The voluptuous schema is restrictive - only the listed values are allowed.

Activity
--------

Here is the validation schema for an activity dataset:

.. code-block:: python

    dataset_schema = Schema({
        "combined production": bool, # More than one reference product
        "exchanges": [Any(elementary_exchange_schema, activity_exchange_schema)],
        "parameters": [valid_parameter],
        'access restricted': valid_access_restriction, # ecospold2 field 3550: accessRestrictedTo
        'economic scenario': str, # ecospold2 field 700: macroEconomicScenarioId
        'end date': str, # Starting and ending dates for dataset validity, in format '2015-12-31'
        'filepath': str,
        'id': str,  # Imported UUID. May not be unique due to allocation.
        Optional("code"): str,  # Guaranteed unique hash code based on attributes
        'location': str, # ecospold2 field 410: shortname
        'name': str, # ecospold2 field 100: activityName
        'start date': str,
        'technology level': valid_technology_levels, # ecospold2 field 500
        'type': valid_activity_types, # ecospold2 field 115: specialActivityType
        Optional('allocation method'): valid_allocation_method,  # Allocation method used. Added by a transformation.
        Optional('reference product'): str, # Name of the reference product. Added by a transformation.
        Optional('suppliers'): list,  # Exchanges which supply a market
    }, required=True)

Technosphere exchanges (``activity_exchange_schema``)
-----------------------------------------------------

.. code-block:: python

    activity_exchange_schema = Schema({
        'amount': float, # ecospold2 field 1020: amount
        'id': str, # ecospold2 field 1005: id
        'name': str, # ecospold2 field 1000: flow name
        'tag': 'intermediateExchange',
        'type': Any('from technosphere', 'reference product', 'byproduct', 'dropped product'),
        'unit': str, # ecospold2 field 1035: unitName
        Optional('activity link'): str, # ecospold2 field 1520: activityLinkId
        Optional('byproduct classification'): valid_byproducts, # ecospold2 field 310: classificationValue, if classificationSystem is 'By-product classification'.
        Optional('conditional exchange'): bool,
        Optional('formula'): str, # ecospold2 field 1060: mathematicalRelation
        Optional('production volume'): valid_production_volume, # Only when needed for multioutput
        Optional('properties'): [valid_property],
        Optional('uncertainty'): valid_uncertainty,
        Optional('variable'): str, # ecospold2_meta field 1040: variableName
    }, required=True)

Biosphere exchanges (``elementary_exchange_schema``)
----------------------------------------------------

.. code-block:: python

    elementary_exchange_schema = Schema({
        'amount': float, # ecospold2 field 1020: amount
        'compartment': str,
        'id': str, # ecospold2 field 1005: id
        'name': str, # ecospold2 field 1000: flow name
        'subcompartment': str,
        'tag': 'elementaryExchange',
        'type': Any('from environment', 'to environment'),
        'unit': str, # ecospold2 field 1035: unitName
        Optional('formula'): str, # ecospold2 field 1060: mathematicalRelation
        Optional('properties'): [valid_property],
        Optional('uncertainty'): valid_uncertainty,
        Optional('variable'): str, # ecospold2_meta field 1040: variableName
    }, required=True)

Parameters
----------

.. code-block:: python

    valid_parameter = Schema({
        "unit": str,
        'amount': float, # ecospold2 field 1710: amount
        'id': str,
        'name': str, # ecospold2 field 1700: name
        Optional('formula'): str, # ecospold2 field 1720: mathematicalRelation
        Optional('uncertainty'): valid_uncertainty,
        Optional('variable'): str, # eocspold2 field 1715: variableName
    })

Properties
----------

.. code-block:: python

    valid_property = Schema({
        'amount': float, # ecospold2 field 2330: amount
        'id': str, # ecospold2 field 2300: propertyId
        'name': str,
        'unit': str, # ecospold2 field 2324: unitName
        'unit': str, # ecospold2 field 2324: unitName
        Optional('formula'): str, # field 2340: mathematicalRelation
        Optional('uncertainty'): valid_uncertainty,
        Optional('variable'): str, # ecospold2 field 2350: variableName
    }, required=True)

Production volume
-----------------

.. code-block:: python

    valid_production_volume = Schema({
        'amount': float, # ecospold2 field 1530: productionVolumeAmount
        Optional('formula'): str, # ecospold2 field 1534: productionVolumeMathematicalRelation
        Optional('uncertainty'): valid_uncertainty,  # ecospold2 field 1539: productionVolumeUncertainty
        Optional('variable'): str, # ecospold2 field 1532: productionVolumeVariableName
    }, required=True)


Metadata
--------

Some fields can only take certain values. The activity dataset, for example, refers to ``valid_activity_types`` and ``valid_access_restriction``. Here are the lists of possible values used in the format definition:

.. code-block:: python

    valid_access_restriction = Any('public', 'licensees', 'results only', 'restricted')

    valid_activity_types = Any("transforming activity", "market activity", "market group",
                               "IO activity", "residual activity", "production mix",
                               "import activity", "supply mix", "export activity",
                               "re-export activity", "correction activity")

     valid_allocation_method = Any(
        'combined production with byproduct',
        'combined production without byproduct',
        'constrained market',
        'economic allocation',
        'no allocation',
        'recycling activity',
        'true value allocation',
        'waste treatment',
    )

    valid_byproducts = Any('allocatable product', 'waste', 'recyclable')

    valid_technology_levels = Any("undefined", "new", "modern",
                                  "current", "old", "outdated")

Uncertainty
-----------

Eight uncertainty distributions can be extracted in Ocelot, though some, such as the gamma and binomial, and not currently used in ecoinvent and therefore are not currently supported. An uncertainty distribution can therefore be any of the following:

.. code-block:: python

    valid_uncertainty = Any(
        valid_beta,
        valid_binomial,
        valid_gamma,
        valid_lognormal,
        valid_normal,
        valid_triangular,
        valid_undefined,
        valid_uniform,
    )

The uncertainty distributions themselves have distribution-specific fields:

.. code-block:: python

    valid_lognormal = Schema({
        'mean': float,
        'pedigree matrix': valid_pedigree_matrix,
        'type': 'lognormal',
        'variance with pedigree uncertainty': float,
        Optional('mu'): float,  # Somehow this is optional (/missing) in some ecospold2 datasets
        Optional('variance'): float,
    }, required=True)

    valid_normal = Schema({
        'mean': float,
        'pedigree matrix': valid_pedigree_matrix,
        'type': 'normal',
        'variance with pedigree uncertainty': float,
        Optional('variance'): float,
    }, required=True)

    valid_uniform = Schema({
        'maximum': float,
        'minimum': float,
        'pedigree matrix': valid_pedigree_matrix,
        'type': 'uniform',
    }, required=True)

    valid_triangular = Schema({
        'maximum': float,
        'minimum': float,
        'mode': float,
        'pedigree matrix': valid_pedigree_matrix,
        'type': 'triangular',
    }, required=True)

    valid_binomial = Schema({
        'n': float,
        'p': float,
        'pedigree matrix': valid_pedigree_matrix,
        'type': 'binomial',
    }, required=True)

    valid_beta = Schema({
        'maximum': float,
        'minimum': float,
        'mode': float,
        'pedigree matrix': valid_pedigree_matrix,
        'type': 'beta',
    }, required=True)

    valid_gamma = Schema({
        'pedigree matrix': valid_pedigree_matrix,
        'scale': float,
        'shape': float,
        'type': 'gamma',
    }, required=True)

    valid_undefined = Schema({
        'maximum': float,
        'minimum': float,
        'pedigree matrix': valid_pedigree_matrix,
        'standard deviation 95%': float,
        'type': 'undefined',
    }, required=True)

The pedigree matrix is a dictionary:

.. code-block:: python

    valid_pedigree_matrix = Any(
        {
            'reliability': int,
            'completeness': int,
            'temporal correlation': int,
            'geographical correlation': int,
            'further technology correlation': int,
        },
        {}  # Empty dictionary is also allowed
    )

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

If the logging information is better represented in a list, they will look like:

.. code-block:: javascript

    {
        type: 'list element',
        data: HTML string
    }
