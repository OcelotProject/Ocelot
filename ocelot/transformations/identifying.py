# -*- coding: utf-8 -*-
from ..errors import IdenticalDatasets
from .utils import activity_hash


CODE_ERROR_MESSAGE = """Found multiple datasets with the attributes:
    Name: {name}
    Reference product: {reference product}
    Unit: {unit}
    Location: {location}
    Start date: {start date}
    End date: {end date}
"""


def add_unique_codes(data):
    """Add the field ``code`` based on unique attributes of datasets.

    Raises ``IdenticalDatasets`` if two datasets with the same attributes were found.

    Uses ``activity_hash``, which hashes the dataset name, reference product, unit, location, start and end date."""
    fields = ("name", "reference product", "unit", "location",
              "start date", "end date")

    seen = set()
    for ds in data:
        code = activity_hash(ds)
        if code in seen:
            processed = {field: ds.get(field) for field in fields}
            raise IdenticalDatasets(CODE_ERROR_MESSAGE.format(**processed))
        else:
            seen.add(code)
        ds['code'] = code
    return data
