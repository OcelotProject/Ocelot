# -*- coding: utf-8 -*-
from . import toolz, data_dir
from .filesystem import get_base_output_directory, create_dir, check_dir
from time import time
import jinja2
import json
import os
import shutil
import uuid


class Report(object):
    """A class that provides a JSON logger during a model run, and formats a nice report afterwards.

    Logs messages are a dictionary with at a minimum the key ``type``. The following types of log messages are understand by the ``Report`` object:

    * Foo
    * Bar

    TODO:

    - Add charts: http://www.chartjs.org/docs/
    - Add media for charts/css
    - Adapt code from ecoinvent-row-report to create static directory and copy JS/CSS over
    - Adapt table code from http://geography.ecoinvent.org/rows/
    - Adapt template from ocelot.space website

    """
    def __init__(self, data):
        report_id = uuid.uuid4().hex
        self.directory = os.path.join(get_base_output_directory(), report_id)
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
            'type': 'report start',
            'time': time(),
            'uuid': report_id
        })
        self.index = 1

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

    def finish(self):
        self.log({
            'type': 'report end',
            'time': time()
        })
        self.logfile.close()
        self.write_report()

    def write_report(self):
        html = HTMLReport(self.fp)
        print("Generated report at: {}".format(self.fp))


def read_json_log(fp):
    with open(fp, encoding='utf-8') as f:
        for line in f:
            yield json.loads(line)


class HTMLReport(object):
    """Generate an HTML report from a :ref:`report` logfile.

    Reports are generated in the same directory as the logfile."""
    def __init__(self, fp):
        base_dir = os.path.abspath(os.path.dirname(fp))
        data = self.read_log(fp)
        self.create_assets_directory(base_dir)
        self.write_page(data, base_dir)
        self.index = 1
        self.data_holder = []

    def read_log(self, fp):
        data = {}
        for line in read_json_log(fp):
            self.handle_line(line, data)
        data['elapsed'] = "{:.1f}".format(data['end'] - data['start'])
        return data

    def write_page(self, data, base_dir):
        template_filepath = os.path.join(data_dir, "report-template.jinja2")
        template = jinja2.Template(open(template_filepath).read())
        with open(os.path.join(base_dir, "report.html"), "w") as f:
            f.write(template.render(**data))

    def create_assets_directory(self, base_dir):
        assets_from_dir = os.path.join(data_dir, "assets")
        assets_to_dir = os.path.join(base_dir, "assets")
        shutil.copytree(assets_from_dir, assets_to_dir)

    def handle_line(self, line, data):
        if line['type'] == 'report start':
            data.update({
                'counts': [line['count']],
                'labels': [],
                'start': line['time'],
                'times': [],
                'uuid': line['uuid'],
            })
        elif line['type'] == 'report end':
            data.update({
                'end': line['time'],
            })
        elif line['type'] == 'function start':
            data['functions'][line] = {
                'start': line['start'],
                ''
            }


# {"type": "start report", "time": 1463249183.372906}
# {"type": "function start", "count": 11552, "time": 1463249183.373087, "description": "Change ``GLO`` locations to ``RoW`` if there are region-specific datasets in the activity group.", "table": [["changed_location", "Location converted to RoW"]], "name": "relabel_global_to_row"}
# {"type": "table element", "data": ["market for fluting medium", ["fluting medium"]]}
# {"type": "table element", "data": ["anti-reflex-coating, etching, solar glass", ["anti-r
