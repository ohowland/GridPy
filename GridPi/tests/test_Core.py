import logging
import unittest
from configparser import ConfigParser

from GridPi.lib import gridpi_core
from GridPi.lib.models import model_core

class TestCoreModule(unittest.TestCase):

    def setUp(self):

        self.test_system = gridpi_core.System()

    def test_add_asset(self):

        self.parser = ConfigParser()
        self.parser.read_dict({'FEEDER':
                                   {'class_name': 'VirtualFeeder',
                                    'name': 'test'}})

        asset_factory = model_core.AssetFactory()  # Create Asset Factory object
        for cfg in self.parser.sections():  # Add models to System, The asset factory acts on a configuration
            self.test_asset = (asset_factory.factory(self.parser[cfg]))
        del asset_factory

        self.test_system.add_asset(self.test_asset)

        self.assertEqual(self.test_asset, self.test_system._assets.assets[0])

    def test_add_process(self):
        pass

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    unittest.main()