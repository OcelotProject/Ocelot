# -*- coding: utf-8 -*-
from .filesystem import get_base_output_directory, create_dir, check_dir
from time import time
import json
import os
import uuid


class Logger(object):
    """The ``Logger`` class provides a JSON logger for use during a model run, and formats a nice report afterwards.

    ``Logger`` provides methods for several types of log messages.

    """
    def __init__(self, data):
        """Initialize the log with the raw extracted data"""
        report_id = uuid.uuid4().hex
        self.directory = self.create_output_directory(report_id)
        self.filepath = os.path.join(self.directory, "report.log.json")
        print("Opening log file at: {}".format(self.filepath))
        self.logfile = open(self.filepath, "w", encoding='utf-8')
        self.log({
            'count': len(data),
            'time': time(),
            'type': 'report start',
            'uuid': report_id,
        })
        self.index = 1

    def create_output_directory(self, report_id):
        directory = os.path.join(get_base_output_directory(), report_id)
        try:
            create_dir(directory)
            assert check_dir(directory)
        except:
            raise OutputDirectoryError(
                "Can't find or write to output directory:\n\t{}".format(
                directory)
            )
        return directory

    def set_index(self, index):
        self.index = index + 1

    def log(self, message):
        self.logfile.write(json.dumps(message) + "\n")

    def start_function(self, metadata, data):
        log_data = {
            'type': 'function start',
            'count': len(data),
            'time': time(),
            'index': self.index,
        }
        log_data.update(metadata)
        self.log(log_data)

    def end_function(self, metadata, data):
        log_data = {
            'type': 'function end',
            'count': len(data),
            'time': time(),
            'index': self.index,
        }
        log_data.update(metadata)
        self.log(log_data)

    def finish(self, show=False):
        self.log({
            'type': 'report end',
            'time': time()
        })
        self.logfile.close()
        print("Generated report at: {}".format(self.filepath))
