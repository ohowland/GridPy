from GridPi import Core
from Models import Models

import unittest
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

        self.assertEqual(self.test_asset, self.test_system._assets['test'])

    def test_add_process(self):
        pass

    def test_add_tagbus(self):
        pass

    def test_register_tags(self):
        pass

    def test_update_tagbus_from_asset(self):
        pass

    def test_write_asset_from_tagbus(self):
        pass

    def write(self):
        pass

    def read(self):
        pass

if __name__ == '__main__':
    unittest.main()