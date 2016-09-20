# -*- coding: utf-8 -*-
from ocelot.logger import create_log, create_detailed_log
import json
import logging
import os
import pytest
import tempfile

base_logger = logging.getLogger('ocelot')
detailed_logger = logging.getLogger('ocelot-detailed')


def test_logging():
    tempdir = tempfile.mkdtemp()
    base_log = create_log(tempdir)
    detailed_log = create_detailed_log(tempdir)

    base_logger.info({"message": 'base logger message'})
    detailed_logger.info({
        "ds": {
            'filepath': os.path.join("foo", "bar", "baz.py"),
            'id': 12345,
            'code': 'abcde'
        },
        "message": 'detailed logger message',
        'function': 'Kalamity Kapers'
    })
    logging.info("Another message")

    with open(os.path.join(tempdir, "report.log.json")) as f:
        base_log = [json.loads(line) for line in f]
    with open(os.path.join(tempdir, "detailed.log.json")) as f:
        detailed_log = [json.loads(line) for line in f]

    assert len(base_log) == 1
    assert base_log[0]['message'] == 'base logger message'

    assert len(detailed_log) == 1
    assert detailed_log[0]['message'] == 'detailed logger message'
    dataset = {
        'code': 'abcde',
        'id': 12345,
        'filename': 'baz.py'
    }
    assert detailed_log[0]['dataset'] == dataset
    assert detailed_log[0]['function'] == 'Kalamity Kapers'
