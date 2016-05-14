# -*- coding: utf-8 -*-
from .configuration import default_configuration
from .filesystem import safe_filename
from .io import extract_directory
from .report import Report
from .utils import get_function_meta
from time import time
import os
import pickle


def SystemModel(data_path, config=None):
    """A system model is a set of assumptions and modeling choices that define how to take a list of unlinked and unallocated datasets, and transform these datasets into a new list of datasets which are linked and each have a single reference product.

    The system model in code is a list of functions. The definition of this list - which functions are included, and in which order - is defined by the :ref:`configuration` object. The input parameter `config` can also be an iterable of functions to be applied. The `SystemModel` does the following:

    * Extract data from the input data sources
    * Initialize a :ref:`report` object
    * Then, for each transforming function in the provided configuration:
        * Log the transforming function start
        * Apply the transforming function
        * Save the intermediate data state
        * Log the transforming function end
    * Finally, write a report.

     """
    config = config or default_configuration
    data = extract_directory(data_path)
    report = Report(data)

    for index, function in enumerate(config):
        metadata = get_function_meta(function)
        report.start_function(metadata, data)
        print("Applying transform {}".format(metadata['name']))
        data = function(data, report)
        dump_fp = os.path.join(report.directory, safe_filename(metadata['name']) + ".pickle")
        with open(dump_fp, "wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        report.end_function(metadata, data)
    report.finish()
