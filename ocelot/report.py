# -*- coding: utf-8 -*-
from . import toolz, data_dir
from .filesystem import get_base_output_directory, create_dir, check_dir
from time import time
import jinja2
import json
import os
import uuid


class Report(object):
    """A class that provides a JSON logger during a model run, and formats a nice report afterwards.

    Logs messages are a dictionary with at a minimum the key ``type``. The following types of log messages are understand by the ``Report`` object:

    * Foo
    * Bar

    """
    def __init__(self, data):
        self.directory = os.path.join(get_base_output_directory(), uuid.uuid4().hex)
        try:
            create_dir(self.directory)
            assert check_dir(self.directory)
        except:
            raise OutputDirectoryError(
                "Can't find or write to output directory:\n\t{}".format(
                self.directory)
            )
        self.fp = os.path.join(self.directory, "report.log.json")
        print("Opening log file at: {}".format(self.fp))
        self.logfile = open(self.fp, "w", encoding='utf-8')
        self.log({
            'type': 'start report',
            'time': time()
        })

    def log(self, message):
        self.logfile.write(json.dumps(message) + "\n")

    def start_function(self, metadata, data):
        log_data = {
            'type': 'function start',
            'count': len(data),
            'time': time(),
        }
        log_data.update(metadata)
        self.log(log_data)

    def end_function(self, metadata, data):
        log_data = {
            'type': 'function end',
            'count': len(data),
            'time': time(),
        }
        log_data.update(metadata)
        self.log(log_data)

    def finish(self):
        self.log({
            'type': 'end report',
            'time': time()
        })
        self.logfile.close()
        self.write_report()

    def write_report(self):
        html = HTMLReport(self.fp)
        print("Generated report at: {}".format(self.fp))


class HTMLReport(object):
    """Generate an HTML report from a :ref:`report` logfile.

    Reports are generated in the same directory as the logfile."""
    def __init__(self, fp):
        self.template_filepath = os.path.join(data_dir, "report-template.jinja2")
        self.data = []
        with open(fp, encoding='utf-8'):
            pass
