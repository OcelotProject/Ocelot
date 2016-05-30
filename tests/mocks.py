# -*- coding: utf-8 -*-
from ocelot.model import system_model
from ocelot.logger import Logger
from unittest import mock
import os
import pytest
import tempfile


class MockLogger(Logger):
    """Test mock that uses a tempfile directory, and deletes it after test runs"""
    def create_output_directory(self, report_id):
        self._tempdir = tempfile.TemporaryDirectory()
        return self._tempdir.name

    def finish(self):
        self.logfile.close()
        self._tempdir.cleanup()


def do_nothing(*args, **kwargs):
    """Mock for `HTMLReport` that doesn't do anything"""
    pass


def passthrough(obj):
    """Mock for `extract_directory` that doesn't do anything"""
    return obj


@pytest.fixture
def fake_report(monkeypatch):
    monkeypatch.setattr(
        'ocelot.model.Logger',
        MockLogger
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
    report, data = system_model([])
    assert data == []
    # Directory not in usual place
    assert "Ocelot" not in report.directory
    # Tempdir is cleaned up
    assert not os.path.exists(report.directory)
