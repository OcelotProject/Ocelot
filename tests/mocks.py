# -*- coding: utf-8 -*-
from ocelot.model import system_model
from ocelot.filesystem import OutputDir
from unittest import mock
import os
import pytest
import tempfile
import uuid


def do_nothing(*args, **kwargs):
    """Mock for `HTMLReport` that doesn't do anything"""
    pass


def passthrough(obj):
    """Mock for ``extract_directory`` that returns the initial input"""
    return obj


@pytest.fixture(scope="function")
def fake_report(monkeypatch):
    tempdir = tempfile.mkdtemp()
    get_fake_directory = lambda : tempdir
    monkeypatch.setattr(
        'ocelot.filesystem.get_base_directory',
        get_fake_directory
    )
    monkeypatch.setattr(
        'ocelot.model.check_cache_directory',
        lambda x: False
    )
    monkeypatch.setattr(
        'ocelot.model.cache_data',
        lambda x, y: None
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
