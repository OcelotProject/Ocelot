from ..model import SystemModel
from ..report import Report
from unittest import mock
import os
import pytest
import tempfile


class MockReport(Report):
    """Test mock that uses a tempfile directory, and deletes it after test runs"""
    def create_output_directory(self, report_id):
        self._tempdir = tempfile.TemporaryDirectory()
        return self._tempdir.name

    def finish(self, show=False):
        self.logfile.close()
        self._tempdir.cleanup()


def passthrough(obj):
    """Mock for `extract_directory` that doesn't do anything"""
    return obj


@pytest.fixture
def fake_report(monkeypatch):
    monkeypatch.setattr(
        'ocelot.model.Report',
        MockReport
    )
    monkeypatch.setattr(
        'ocelot.model.extract_directory',
        passthrough
    )


def test_report_and_extract_directory_mock(fake_report):
    report = SystemModel([])
    # Directory not in usual place
    assert "Ocelot" not in report.directory
    # Tempdir is cleaned up
    assert not os.path.exists(report.directory)
