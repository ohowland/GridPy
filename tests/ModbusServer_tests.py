from nose.tools import *
import NAME


def setup(): # Runs before every test method.
	print 'Setup.'

def teardown(): # Runs after every test method.
	print 'Cleanup.'

def testbasic():
	print 'Test 1 Ran.'