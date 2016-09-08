# -*- coding: utf-8 -*-
try:
    import brightway2 as bw2
    from bw2io.importers.base_lci import LCIImporter
except ImportError:
    bw2 = None


class Brightway2Converter:
    """Convert a database to the Brightway2 format.

    Requires `Brightway2 <https://brightwaylca.org/>`__ to be installed alongside Ocelot.

    The formats are `quite <https://docs.ocelot.space/data_format.html>`__ `similar <https://docs.brightwaylca.org/intro.html#activity-data-format>`__, but a few things do need to be fixed. We also remove some data that is not useful after Ocelot produces a linked database.

    Currently, this class does not include uncertainty.

    Turns technosphere exchanges into the following:

    .. code-block:: python

        {
            'input': (database_name, code),
            'amount': float,
            'name': name,
            'unit': unit,
            'type': 'technosphere',
        }

    Turns biosphere exchanges into the following:

    .. code-block:: python

        {
            'amount': float,
            'name': name,
            'categories': (tuple_of_categories),
            'unit': unit,
            'type': 'biosphere',
        }

    Biosphere exchanges will still need to be linked to the background biosphere database. This can be done manually, but is done for you in the function ``import_into_brightway2``.

    Biosphere exchanges can be either from or to the environment. We assume that the sign is already correct for the purposes of inventory and impact assessment calculations. Both types are treated as biosphere exchanges with any numerical modifications.

    Turns production exchanges (reference products) into the following:

    .. code-block:: python

        {
            'input': (database_name, code),
            'amount': float,
            'type': 'production',
        }

    Currently, Brightway2 has a strong assumption that a product is associated with one production activity. To handle the production of byproducts which are kept in datasets (e.g. our handling of the consequential model), we have to pretend that these productions are negative inputs. Each byproduct must already be linked to an alternative producer in any case, so this shift has no effect on the matrix - it only translates exchanges into something that Brightway2 can understand.

    Therefore, byproduct production exchanges are turned into the following:

    .. code-block:: python

        {
            'input': (database_name, code),
            'amount': -1 * original_amount,
            'type': 'technosphere',
        }

    Finally, we only include some elements of the activity datasets themselves. The following keys from activity datasets are included:

        * name
        * location
        * economic scenario
        * start date
        * end date
        * technology level
        * filepath
        * code

    In addition, the field ``database`` is added.

    """
    @staticmethod
    def convert_to_brightway2(data, database_name):
        # TODO: Ensure database is SOUPy and has codes
        # TODO: Translate uncertainty types
        return (Brightway2Converter.translate_activity(ds) for ds in data)

    @staticmethod
    def translate_activity(ds, database_name):
        EXCHANGE_MAPPING = {
            'reference product': Brightway2Converter.translate_technosphere_exchange,
            'byproduct': Brightway2Converter.translate_byproduct_exchange,
            'from technosphere': Brightway2Converter.translate_technosphere_exchange,
            'from environment': Brightway2Converter.translate_biosphere_exchange,
            'to environment': Brightway2Converter.translate_biosphere_exchange
        }
        FIELDS = ("code", "economic scenario", "end date", "filepath",
                  "location", "name", "start date", "technology level")
        data = {field: ds[field]}
        data['exchanges'] = [EXCHANGE_MAPPING[exc['type']](exc) for exc in ds['exchanges']]
        return data

    @staticmethod
    def translate_biosphere_exchange(exc, database_name):
        return {
            'type': "biosphere",
            'amount': exc['amount'],
            'name': exc['name'],
            'unit': exc['unit'],
            'categories': (exc['compartment'], exc['subcompartment'])
        }

    def translate_technosphere_exchange(exc, database_name):
        return {
            'type': "production",
            'amount': exc['amount'],
            'input': (database_name, exc['code'])
        }

    def translate_production_exchange(exc, database_name):
        return {
            'type': "production",
            'amount': exc['amount'],
            'input': (database_name, exc['code'])
        }

    def translate_byproduct_exchange(exc, database_name):
        return {
            'type': "technosphere",
            'amount': -1 * exc['amount'],
            'input': (database_name, exc['code'])
        }


def import_into_brightway2(data, database_name):
    """Import an Ocelot linked database into a Brightway2 project.

    Make sure you in the **correct project** before running this function!

    Arguments:

        * ``data`` (list): Database output from Ocelot system model
        * ``database_name`` (str): Name of new database. Should not already exist in the current project.

    """
    if not bw2:
        raise ImportError("Brightway2 not found")
    print("Creating database {} in project {}".format(
        database_name, bw2.projects.current)
    )
    assert database_name not in bw2.databases
    data = list(Brightway2Converter.convert_to_brightway2(data, database_name))
    importer = LCIImporter(database_name)
    importer.data = data
    importer.match_database("biosphere3")
    print(importer.statistics())
    return importer

