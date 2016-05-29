# -*- coding: utf-8 -*-
from . import data_dir
import jinja2
import json
import os
import pathlib
import shutil
import webbrowser


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
    """Generate an HTML report from a :ref:`logger` logfile.

    Reports are generated in the same directory as the logfile.

    Takes the log filepath as input variable ``filepath``. A second optional input, ``show``, will open the generated report in a new webbrowser tab if ``True``.

    """
    def __init__(self, filepath, show=False):
        base_dir = os.path.abspath(os.path.dirname(filepath))
        data = self.read_log(filepath)
        self.create_assets_directory(base_dir)
        self.write_page(data, base_dir)
        self.index = 0
        if show:
            self.show_in_webbrowser()

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
        if os.path.exists(assets_to_dir):
            shutil.rmtree(assets_to_dir)
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

