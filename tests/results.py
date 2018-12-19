# -*- coding: utf-8 -*-
from ocelot.results import SaveStrategy
import pytest

def test_default_save_strategy():
    ss = SaveStrategy()
    assert ss(0)
    assert ss(1000)
    assert not ss(1)

def test_index_as_int():
    ss = SaveStrategy(2)
    assert ss(0)
    assert ss(2)
    assert not ss(1)

def test_index_as_string():
    ss = SaveStrategy(2)
    assert ss(0)
    assert ss(2)
    assert not ss(1)

def test_invalid_index():
    with pytest.raises(ValueError):
        SaveStrategy("a")
    with pytest.raises(ValueError):
        SaveStrategy(0)
    with pytest.raises(ValueError):
        SaveStrategy(-1)
    with pytest.raises(ValueError):
        SaveStrategy("0")

def test_simple_range():
    ss = SaveStrategy("2:7")
    assert not ss(-1)
    assert not ss(0)
    assert not ss(1)
    assert ss(2)
    assert ss(3)
    assert ss(7)
    assert not ss(8)

def test_range_step():
    ss = SaveStrategy("2:10:3")
    assert not ss(-1)
    assert not ss(0)
    assert not ss(1)
    assert ss(2)
    assert not ss(3)
    assert ss(5)
    assert not ss(6)
    assert not ss(10)
    assert not ss(11)
    ss = SaveStrategy("2:11:3")
    assert ss(11)

def test_invalid_range():
    with pytest.raises(ValueError):
        SaveStrategy("1:")
    with pytest.raises(ValueError):
        SaveStrategy(":")
    with pytest.raises(ValueError):
        SaveStrategy("1:2:")
    with pytest.raises(ValueError):
        SaveStrategy("1:2:a")
