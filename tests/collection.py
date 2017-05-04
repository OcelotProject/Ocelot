# -*- coding: utf-8 -*-
from ocelot.collection import Collection, unwrap_functions
from ocelot.filesystem import OutputDir
from ocelot.model import system_model
from unittest import mock
import os
import pytest
import tempfile
import uuid


def do_nothing(*args, **kwargs):
    """Mock for `HTMLReport` that doesn't do anything"""
    pass

def passthrough(obj, use_cache=True):
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

def test_report_and_extract_directory_mock(fake_report):
    output_dir, data = system_model([])
    assert data == []
    # Directory not in usual place
    assert "Ocelot" not in output_dir.directory

def test_empty_collection(fake_report):
    empty_collection = Collection("0")
    report, data = system_model([1,2,3,4], [empty_collection])
    assert data == [1,2,3,4]

def test_can_pass_collection_directly(fake_report):
    """i.e. not in a list"""
    collection = Collection("l", lambda x: x)
    report, data = system_model([1,2,3,4], collection)
    assert data == [1,2,3,4]

def test_can_nest_collections(fake_report):
    empty_collection = Collection("0")
    report, data = system_model([1,2,3,4], [Collection("0", empty_collection)])
    assert data == [1,2,3,4]

def test_empty_collection_is_falsey():
    """Passing a bare empty collection will trigger the default configuration"""
    assert not bool(Collection("foo"))

def test_collection_applied_in_order(fake_report):
    collection = Collection(
        "foo",
        lambda x: x + [1],
        lambda x: x + [2]
    )
    report, data = system_model([], collection)
    assert data == [1,2]

def test_list_of_functions_also_possible(fake_report):
    list_of_functions = [
        lambda x: x + [1],
        lambda x: x + [2]
    ]
    report, data = system_model([], list_of_functions)
    assert data == [1,2]

def test_collection_len():
    collection = Collection("1", 1, 2)
    assert len(collection) == 2

def test_collection_contains():
    collection = Collection("1", 1, 2)
    assert 1 in collection
    assert 3 not in collection

def test_collection_unwrapped():
    collection = Collection("foo", 1, 2, Collection("bar", 3, 4))
    assert collection.functions == [1,2,3,4]

def test_collection_getitem():
    collection = Collection("foo", 1, 2, 3)
    assert collection[1] == 2

def test_collection_setitem():
    collection = Collection("foo", 1, 2, 3)
    collection[2] = 'bar'
    assert collection.functions == [1, 2, 'bar']

def test_collection_deltiem():
    collection = Collection("foo", 1, 2, 3)
    del collection[1]
    assert collection.functions == [1, 3]

def test_collection_insert():
    collection = Collection("foo", 1, 2, 3)
    collection.insert(0, 'foo')
    assert collection.functions == ['foo', 1, 2, 3]

def test_collection_reversed():
    collection = Collection("foo", 1, 2, 3)
    assert list(reversed(collection)) == [3, 2, 1]

def test_collection_str():
    collection = Collection("foo", 1, 2, 3)
    assert str(collection) == 'Collection foo with 3 functions'
    assert repr(collection) == 'Collection foo with 3 functions'

def test_unwrap_functions():
    a = lambda x: False
    b = lambda x: False
    c = lambda x: False
    d = lambda x: False
    e = lambda x: False

    lst = [a, Collection("b", b, Collection("c", c, d)), e]
    assert unwrap_functions(lst) == [a, b, c, d, e]
