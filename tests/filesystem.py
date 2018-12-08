# -*- coding: utf-8 -*-
from ocelot.filesystem import (
    cache_data,
    check_cache_directory,
    get_base_directory,
    get_cache_directory,
    get_from_cache,
    get_output_directory,
)
import os
import pytest
import random
import tempfile
import time


def test_base_directory():
    assert get_base_directory()

def test_output_directory():
    assert get_output_directory()

def test_output_directory_envvar():
    os.environ["OCELOT_OUTPUT"] = os.getcwd()
    assert get_output_directory() == os.getcwd()

def test_cache_directory():
    assert get_cache_directory()

def test_cache_directory_error(monkeypatch):
    monkeypatch.setattr(
        'ocelot.filesystem.get_cache_filepath_for_data_path',
        lambda x: "not a real thing"
    )
    assert not check_cache_directory(os.getcwd())

def test_directory_structure():
    base = get_base_directory()
    output = get_output_directory()
    cache = get_cache_directory()
    assert "cache" in cache
    assert base in cache
    # Could be an env. variable
    if "model-runs" in output:
        assert base in output

@pytest.fixture
def fake_output_dir(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr(
            'ocelot.filesystem.get_base_directory',
            lambda: os.path.abspath(tmpdir)
        )
        yield tmpdir

def test_fake_output_dir_fixture(fake_output_dir):
    assert "Ocelot" not in get_cache_directory()

def test_cache_loading(fake_output_dir):
    random_data = {k: random.randint(0, 10) for k in "abcdefghijklmnop"}
    fp = os.path.abspath(__file__)
    cache_data(random_data, fp)
    assert random_data == get_from_cache(fp)

def test_cache_expiration(fake_output_dir):
    new_file = os.path.join(fake_output_dir, "test.file")
    with open(new_file, "w") as f:
        f.write("foo")
    random_data = {k: random.randint(0, 10) for k in "abcdefghijklmnop"}
    cache_data(random_data, fake_output_dir)
    time.sleep(0.5)
    with open(new_file, "w") as f:
        f.write("bar")
    assert not check_cache_directory(fake_output_dir)
