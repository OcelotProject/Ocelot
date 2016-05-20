# -*- coding: utf-8 -*-
from . import toolz, data_dir
from .filesystem import get_base_output_directory, create_dir, check_dir
from time import time
import jinja2
import json
import os
import pathlib
import shutil
import uuid
import webbrowser


class Report(object):
    """A class that provides a JSON logger during a model run, and formats a nice report afterwards.

    Logs messages are a dictionary with at a minimum the key ``type``. The following types of log messages are understand by the ``Report`` object:

    * Foo
    * Bar

    TODO:
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
            'count': len(data),
            'time': time(),
            'type': 'report start',
            'uuid': report_id,
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

    def finish(self, show=False):
        self.log({
            'type': 'report end',
            'time': time()
        })
        self.logfile.close()
        self.write_report()
        if show:
            self.html.show_in_webbrowser()

    def write_report(self):
        self.html = HTMLReport(self.fp)
        print("Generated report at: {}".format(self.fp))


def read_json_log(fp):
    with open(fp, encoding='utf-8') as f:
        for line in f:
            yield json.loads(line)


def jsonize(data):
    """Convert some values to JSON strings and do a few other manipulations"""
    _ = lambda x: json.dumps(x, ensure_ascii=False)
    data['count_labels'] = _([x[0] for x in data['counts']])
    data['count_data'] = _([x[1] for x in data['counts']])
    data['time_labels'] = _([x[0] for x in data['times']])
    data['time_data'] = _([x[1] for x in data['times']])
    for k, v in data['functions'].items():
        if hasattr(v, "tabledata"):
            v["tabledata"] = _(sorted(v["tabledata"]))
            v['table']['columns'] = _(v['table']['columns'])
        v['index'] = k
    data['functions'] = list(data['functions'].values())
    data['functions'].sort(key=lambda x: x['index'])
    return data


class HTMLReport(object):
    """Generate an HTML report from a :ref:`report` logfile.

    Reports are generated in the same directory as the logfile."""
    def __init__(self, fp):
        base_dir = os.path.abspath(os.path.dirname(fp))
        data = self.read_log(fp)
        self.create_assets_directory(base_dir)
        self.write_page(data, base_dir)
        self.index = 0

    def show_in_webbrowser(self):
        webbrowser.open_new_tab(
            pathlib.Path(self.report_fp).as_uri()
        )

    def read_log(self, fp):
        data = {'functions': {}}
        for line in read_json_log(fp):
            self.handle_line(line, data)
        data['elapsed'] = "{:.1f}".format(data['times'][-1][1] - data['times'][0][1])
        data['times'] = [(x, y - data['times'][0][1]) for x, y in data['times']]
        return jsonize(data)

    def write_page(self, data, base_dir):
        template_filepath = os.path.join(data_dir, "report-template.jinja2")
        template = jinja2.Template(open(template_filepath).read())
        self.report_fp = os.path.join(base_dir, "report.html")
        with open(self.report_fp, "w") as f:
            f.write(template.render(**data))

    def create_assets_directory(self, base_dir):
        assets_from_dir = os.path.join(data_dir, "assets")
        assets_to_dir = os.path.join(base_dir, "assets")
        shutil.copytree(assets_from_dir, assets_to_dir)

    def handle_line(self, line, data):
        if line['type'] == 'report start':
            data.update({
                'counts': [("Start", line['count'])],
                'times': [("Start", line['time'])],
                'uuid': line['uuid'],
            })
        elif line['type'] == 'report end':
            data['times'].append(('End', line['time']))
        elif line['type'] == 'function start':
            self.index = line['index']
            data['functions'][self.index] = {
                'start': line['time'],
            }
            if line['table']:
                data['functions'][self.index]['tabledata'] = []
        elif line['type'] == 'function end':
            data['counts'].append((line['name'], line['count']))
            data['times'].append((line['name'], line['time']))
            data['functions'][self.index].update({
                'time': line['time'] - data['functions'][self.index]['start'],
                'end': line['time'],
                'count': line['count'],
                'name': line['name'],
                'id': 'function{}'.format(self.index),
                'description': line['description'],
                'table': line['table'],
            })
        elif line['type'] == 'table element':
            data['functions'][self.index]['tabledata'].append(line['data'])

