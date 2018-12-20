# -*- coding: utf-8 -*-
from .configuration import cutoff_config
from .filesystem import (
    cache_data,
    OutputDir,
    save_intermediate_result,
    save_specific_dataset,
)
from .io import extract_directory
from .logger import create_log, create_detailed_log
from .report import HTMLReport
from .results import SaveStrategy
from .utils import get_function_meta, validate_configuration
from collections.abc import Iterable
import itertools
import logging
import shutil
import sys
import wrapt

logger = logging.getLogger('ocelot')


def apply_transformation(function, counter, data, output_dir, save_strategy, follow):
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
        logger.info(metadata)

        print("Applying transformation {}".format(metadata['name']))
        data = function(data)
        metadata.update(
            type="function end",
            count=len(data)
        )

        if save_strategy(index):
            save_intermediate_result(output_dir, index, data, metadata['name'])

        if follow:
            save_specific_dataset(output_dir, index, data,
                                  follow, metadata['name'])

        logger.info(metadata)
        return data


def system_model(data_path, config=None, show=False, use_cache=True,
                 save_strategy=None, follow=None):
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

    Args:

        * ``datapath``: Filepath to directory of undefined dataset files.
        * ``config``: System model choice. Default is cutoff system model.
        * ``show``: Boolean flag to open the final report in a web browser after model completion.
        * ``use_cache``: Boolean flag to use cached data instead of raw ecospold2 files when possible.
        * ``save_strategy``: Optional input argument to initialize a ``SaveStrategy``.
        * ``follow``: Optional filename of a file to follow (i.e. save after each transformation function) during system model execution.

    Returns:

        * An ``OutputDir`` object which tells you where the report was generated
        * The final version of the data in a list

    """
    print("Starting Ocelot model run")
    config = validate_configuration(config or cutoff_config)
    data = extract_directory(data_path, use_cache)
    output_manager = OutputDir(follow=follow)
    try:
        counter = itertools.count()
        logfile_path = create_log(output_manager.directory)
        create_detailed_log(output_manager.directory)

        print("Opening log file at: {}".format(logfile_path))

        logger.info({
            'type': 'report start',
            'uuid': output_manager.report_id,
            'count': len(data),
        })

        save_strategy = SaveStrategy(save_strategy)

        for obj in config:
            data = apply_transformation(obj, counter, data,
                                        output_manager.directory,
                                        save_strategy, follow)

        print("Saving final results")
        save_intermediate_result(output_manager.directory, "final-results", data)

        logger.info({'type': 'report end'})
        print(("Compare results with: ocelot-compare compare {} "
               "<reference results>").format(output_manager.report_id))
        HTMLReport(logfile_path, show)
        return output_manager, data

    except KeyboardInterrupt:
        print("Terminating Ocelot model run")
        print("Deleting output directory:\n{}".format(output_manager.directory))
        shutil.rmtree(output_manager.directory)
        sys.exit(1)
