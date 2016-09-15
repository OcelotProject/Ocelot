# -*- coding: utf-8 -*-
__all__ = (
    "extract_directory",
    "cleanup_data_directory",
    "dataset_schema",
    "validate_directory",
    "validate_directory_against_xsd",
)

from .extract_ecospold2 import extract_ecospold2_directory
from ..filesystem import check_cache_directory, get_from_cache, cache_data


def extract_directory(data_path, use_cache=True, use_mp=True):
    """Extract ecospold2 files in directory ``dirpath``.

    Uses and writes to cache if ``use_cache`` is ``True``.

    Returns datasets in Ocelot internal format."""
    if not use_cache:
        return extract_ecospold2_directory(data_path, use_mp)
    elif check_cache_directory(data_path):
        print("Using cached ecospold2 data")
        return get_from_cache(data_path)
    else:
        data = extract_ecospold2_directory(data_path, use_mp)
        cache_data(data, data_path)
    return data

from .cleanup import cleanup_data_directory
from .validate_ecospold2 import validate_directory_against_xsd, validate_directory
from .validate_internal import dataset_schema
