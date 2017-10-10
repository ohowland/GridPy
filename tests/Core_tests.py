from nose.tools import *

from Core.Core import System
from Core.Models import Asset

def setup(): # Runs before every test method.
    print('Setup.')


def teardown(): # Runs after every test method.
	print('Cleanup.')

@with_setup(setup, teardown)
def testconfig1():
    test_system = System()
    asset1 = Asset()
    test_system.add_asset(asset1)
    print('Test 1 Ran.')

