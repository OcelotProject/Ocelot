# -*- coding: utf-8 -*-
from .configuration import default_configuration
from .filesystem import safe_filename, OutputDir
from .io import extract_directory
from .logger import create_log
from .report import HTMLReport
from .utils import get_function_meta
from collections.abc import Iterable
from time import time
import itertools
import logging
import os
import pickle
import shutil
import sys


def apply_transformation(function, counter, data, output_dir):
    # A `function` can be a list of functions
    if isinstance(function, Iterable):
        for obj in function:
            data = apply_transformation(obj, counter, data, output_dir)
        return data
    else:
        metadata = get_function_meta(function)
        index = next(counter)
        metadata.update(
            index=index,
            type="function start",
            count=len(data),
        )
        logging.info(metadata)

        print("Applying transformation {}".format(metadata['name']))
        data = function(data)
        dump_fp = os.path.join(
            output_dir,
            "{}.".format(index) + safe_filename(metadata['name']) + ".pickle"
        )
        with open(dump_fp, "wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        metadata.update(
            type="function end",
            count=len(data)
        )
        logging.info(metadata)
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
    print("Starting Ocelot model run")
    try:
        config = config or default_configuration
        data = extract_directory(data_path)
        output_manager = OutputDir()
        counter = itertools.count()
        logfile_path = create_log(output_manager.directory)
        print("Opening log file at: {}".format(logfile_path))

        logging.info({
            'type': 'report start',
            'uuid': output_manager.report_id,
            'count': len(data),
        })

        for obj in config:
            data = apply_transformation(obj, counter, data,
                                        output_manager.directory)

        logging.info({'type': 'report end'})

        html = HTMLReport(logfile_path, show)

        return output_manager, data
    except KeyboardInterrupt:
        print("Terminating Ocelot model run")
        print("Deleting output directory:\n{}".format(output_manager.directory))
        shutil.rmtree(output_manager.directory)
        sys.exit(1)
