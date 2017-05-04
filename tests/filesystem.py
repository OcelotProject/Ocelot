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


class TempDir(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.dp = tempfile.mkdtemp()

    def __call__(self):
        return self.dp

tempdir = TempDir()


@pytest.fixture
def fake_output_dir(monkeypatch):
    monkeypatch.setattr(
        'ocelot.filesystem.get_base_directory',
        tempdir
    )


def test_fake_output_dir_fixture(fake_output_dir):
    tempdir.reset()
    assert "Ocelot" not in get_cache_directory()

def test_cache_loading(fake_output_dir):
    tempdir.reset()
    random_data = {k: random.randint(0, 10) for k in "abcdefghijklmnop"}
    fp = os.path.abspath(__file__)
    cache_data(random_data, fp)
    assert random_data == get_from_cache(fp)

def test_cache_expiration(fake_output_dir):
    tempdir.reset()
    new_dp = tempfile.mkdtemp()
    new_file = os.path.join(new_dp, "test.file")
    with open(new_file, "w") as f:
        f.write("foo")
    random_data = {k: random.randint(0, 10) for k in "abcdefghijklmnop"}
    cache_data(random_data, new_dp)
    time.sleep(0.5)
    with open(new_file, "w") as f:
        f.write("bar")
    assert not check_cache_directory(new_dp)

