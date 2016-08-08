# -*- coding: utf-8 -*-
from ocelot.filesystem import (
    get_base_directory,
    get_cache_directory,
    get_output_directory,
)


def test_base_directory():
    assert get_base_directory()

def test_output_directory():
    assert get_output_directory()

def test_cache_directory():
    assert get_cache_directory()

def test_directory_structure():
    base = get_base_directory()
    output = get_output_directory()
    cache = get_cache_directory()
    assert "cache" in cache
    assert base in cache
    # Could be an env. variable
    if "model-runs" in output:
        assert base in output
