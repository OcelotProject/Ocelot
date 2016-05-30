# -*- coding: utf-8 -*-
from .configuration import default_configuration
from .filesystem import safe_filename
from .io import extract_directory
from .logger import Logger
from .report import HTMLReport
from .utils import get_function_meta
from collections.abc import Iterable
from time import time
import itertools
import os
import pickle
import shutil
import sys


def apply_transformation(function, counter, logger, data):
    if isinstance(function, Iterable):
        for obj in function:
            data = apply_transformation(obj, counter, logger, data)
        return data
    else:
        metadata = get_function_meta(function)
        index = next(counter)
        logger.set_index(index)
        logger.start_function(metadata, data)
        print("Applying transformation {}".format(metadata['name']))
        data = function(data, logger)
        dump_fp = os.path.join(
            logger.directory,
            "{}.".format(index) + safe_filename(metadata['name']) + ".pickle"
        )
        with open(dump_fp, "wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        logger.end_function(metadata, data)
        return data


def system_model(data_path, config=None, show=False):
    """A system model is a set of assumptions and modeling choices that define how to take a list of unlinked and unallocated datasets, and transform these datasets into a new list of datasets which are linked and each have a single reference product.

    The system model itself is a list of functions. The definition of this list - which functions are included, and in which order - is defined by the input parameter ``config``, which can be a list of functions or a :ref:`configuration` object. The ``system_model`` does the following:

    * Extract data from the input data sources
    * Initialize a :ref:`logger` object
    * Then, for each transformation function in the provided configuration:
        * Log the transformation function start
        * Apply the transformation function
        * Save the intermediate data state
        * Log the transformation function end
    * Finally, write a report.

    """
    config = config or default_configuration
    data = extract_directory(data_path)
    logger = Logger(data)
    print("Starting Ocelot model run")
    try:
        counter = itertools.count()

        for obj in config:
            data = apply_transformation(obj, counter, logger, data)

        logger.finish()
        html = HTMLReport(logger.filepath, show)

        return logger, data
    except KeyboardInterrupt:
        print("Terminating Ocelot model run")
        print("Deleting output directory:\n{}".format(logger.directory))
        shutil.rmtree(logger.directory)
        sys.exit(1)
