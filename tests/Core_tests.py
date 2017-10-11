from nose.tools import *
import unittest

from GridPi.Core import System
from GridPi.Models import Asset

def setup_func():
    "set up test fixtures"
    pass

def teardown_func():
    "tear down test fixtures"
    pass

@with_setup(setup_func, teardown_func)
def test_add_asset():
    system = System()
    asset = Asset()
    system.add_asset(asset)
    assert True

@with_setup(setup_func, teardown_func)
def test_remove_asset():
    system = System()
    asset = Asset()
    system.add_asset(asset)
    assert True

