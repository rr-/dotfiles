import os
import sys
import unittest

here = os.path.dirname(__file__)
loader = unittest.defaultTestLoader

def suite():
	suite = unittest.TestSuite()
	for fn in os.listdir(here):
		if fn.startswith('test') and fn.endswith('.py'):
			mod_name = 'lib.test.' + fn[:-3]
			__import__(mod_name)
			module = sys.modules[mod_name]
			suite.addTest(loader.loadTestsFromModule(module))
	return suite

if __name__ == '__main__':
	unittest.main(defaultTest='suite')
