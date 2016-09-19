# -*- coding: utf-8 -*-
import json
import logging
import os
import time


class JsonFormatter(logging.Formatter):
    """Uses code from https://github.com/madzak/python-json-logger/ under BSD license"""
    def format(self, record):
        assert isinstance(record.msg, dict)
        message_dict = record.msg
        message_dict['time'] = time.time()
        return json.dumps(message_dict, ensure_ascii=False)


class DatasetJsonFormatter(logging.Formatter):
    def format(self, record):
        """Format message for easy filtering by dataset attributes.

        Extracts the following from the dataset:

        * filename
        * id
        * code

        """
        assert isinstance(record.msg, dict)
        ds = record.msg['ds']
        message_dict = {
            'time': time.time(),
            'message': record.msg['message'],
            'function': record.msg['function'],
            'dataset': {
                'id': ds.get('id'),
                'filename': os.path.basename(ds.get('filepath', '')),
                'code': ds.get('code')
            }
        }
        return json.dumps(message_dict, ensure_ascii=False)


def create_log(output_dir):
    logger = logging.getLogger('ocelot')
    logger.propagate = False
    formatter = JsonFormatter()
    filepath = os.path.join(output_dir, "report.log.json")
    handler = logging.FileHandler(filepath, encoding='utf-8')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return filepath


def create_detailed_log(output_dir):
    logger = logging.getLogger('ocelot-detailed')
    logger.propagate = False
    formatter = DatasetJsonFormatter()
    filepath = os.path.join(output_dir, "detailed.log.json")
    handler = logging.FileHandler(filepath, encoding='utf-8')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return filepath
