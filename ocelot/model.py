# -*- coding: utf-8 -*-
from .configuration import default_configuration
from .filesystem import (
    cache_data,
    check_cache_directory,
    OutputDir,
    save_intermediate_result,
)
from .io import extract_directory
from .logger import create_log
from .report import HTMLReport
from .results import SaveStrategy
from .utils import get_function_meta, validate_configuration
from collections.abc import Iterable
import itertools
import logging
import os
import shutil
import sys
import wrapt


def apply_transformation(function, counter, data, output_dir, save_strategy):
    # A `function` can be a list of functions
    if (isinstance(function, Iterable)
        and not isinstance(function, wrapt.FunctionWrapper)):
        for obj in function:
            data = apply_transformation(obj, counter, data,
                                        output_dir, save_strategy)
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
        metadata.update(
            type="function end",
            count=len(data)
        )

        if save_strategy(index):
            save_intermediate_result(output_dir, index, data, metadata['name'])
        logging.info(metadata)
        return data


def system_model(data_path, config=None, show=False, use_cache=True, save_strategy=None):
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

    Can be interrupted with CTRL-C. Interrupting will delete the partially completed report.

    Returns:

        * An ``OutputDir`` object which tells you where the report was generated
        * The final version of the data in a list

    """
    print("Starting Ocelot model run")
    try:
        config = validate_configuration(config or default_configuration)
        data = extract_directory(data_path, use_cache)
        output_manager = OutputDir()
        counter = itertools.count()
        logfile_path = create_log(output_manager.directory)
        print("Opening log file at: {}".format(logfile_path))

        logging.info({
            'type': 'report start',
            'uuid': output_manager.report_id,
            'count': len(data),
        })

        save_strategy = SaveStrategy(save_strategy)

        for obj in config:
            data = apply_transformation(obj, counter, data,
                                        output_manager.directory,
                                        save_strategy)

        print("Saving final results")
        save_intermediate_result(output_manager.directory, "final-results", data)

        logging.info({'type': 'report end'})

        html = HTMLReport(logfile_path, show)

        return output_manager, data
    except KeyboardInterrupt:
        print("Terminating Ocelot model run")
        print("Deleting output directory:\n{}".format(output_manager.directory))
        shutil.rmtree(output_manager.directory)
        sys.exit(1)
