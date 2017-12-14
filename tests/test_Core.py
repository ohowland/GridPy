from GridPi import Core
from Models import Models

import unittest
import logging
from configparser import ConfigParser

class TestCoreModule(unittest.TestCase):

    def setUp(self):

        self.test_system = Core.System()

    def test_add_asset(self):

        self.parser = ConfigParser()
        self.parser.read_dict({'FEEDER':
                                   {'class_name': 'VirtualFeeder',
                                    'name': 'test'}})

        asset_factory = Models.AssetFactory()  # Create Asset Factory object
        for cfg in self.parser.sections():  # Add Models to System, The asset factory acts on a configuration
            self.test_asset = (asset_factory.factory(self.parser[cfg]))
        del asset_factory

        self.test_system.add_asset(self.test_asset)

        self.assertEqual(self.test_asset, self.test_system._assets[0])

    def test_add_process(self):
        pass

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    unittest.main()