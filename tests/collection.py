# -*- coding: utf-8 -*-
from ocelot.collection import Collection
from ocelot.model import system_model
from .mocks import fake_report

# Tests for `Collection` of functions


def test_empty_collection(fake_report):
    empty_collection = Collection()
    report, data = system_model([1,2,3,4], [empty_collection])
    assert data == [1,2,3,4]

def test_can_pass_collection_directly(fake_report):
    """i.e. not in a list"""
    collection = Collection(lambda x, y: x)
    report, data = system_model([1,2,3,4], collection)
    assert data == [1,2,3,4]

def test_can_nest_collections(fake_report):
    empty_collection = Collection()
    report, data = system_model([1,2,3,4], Collection(empty_collection))
    assert data == [1,2,3,4]

def test_empty_collection_is_falsey():
    """Passing a bare empty collection will trigger the default configuration"""
    assert not bool(Collection())

def test_collection_applied_in_order(fake_report):
    collection = Collection(
        lambda x, y: x + [1],
        lambda x, y: x + [2]
    )
    report, data = system_model([], collection)
    assert data == [1,2]

def test_list_of_functions_also_possible(fake_report):
    list_of_functions = [
        lambda x, y: x + [1],
        lambda x, y: x + [2]
    ]
    report, data = system_model([], list_of_functions)
    assert data == [1,2]

def test_collection_len():
    collection = Collection(1, 2)
    assert len(collection) == 2

def test_collection_contains():
    collection = Collection(1, 2)
    assert 1 in collection
    assert 3 not in collection
