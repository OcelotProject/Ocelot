# -*- coding: utf-8 -*-
from ocelot.model import system_model
from ocelot.filesystem import OutputDir
from unittest import mock
import os
import pytest
import tempfile
import uuid


class MockOutputDir(object):
    """Test mock that uses a tempfile directory, and deletes it after test runs"""
    def __init__(self, *args, **kwargs):
        self.report_id = uuid.uuid4().hex
        self.directory = tempfile.mkdtemp()
        print("Created:")
        print(self.directory)
        print(os.path.exists(self.directory))

def do_nothing(*args, **kwargs):
    """Mock for `HTMLReport` that doesn't do anything"""
    pass


def passthrough(obj):
    """Mock for `extract_directory` that doesn't do anything"""
    return obj


@pytest.fixture
def fake_report(monkeypatch):
    monkeypatch.setattr(
        'ocelot.model.OutputDir',
        MockOutputDir
    )
    monkeypatch.setattr(
        'ocelot.model.extract_directory',
        passthrough
    )
    monkeypatch.setattr(
        'ocelot.model.HTMLReport',
        do_nothing
    )

# Test to make sure above fixture correctly monkey-patches stuff

def test_report_and_extract_directory_mock(fake_report):
    output_dir, data = system_model([])
    assert data == []
    # Directory not in usual place
    assert "Ocelot" not in output_dir.directory
