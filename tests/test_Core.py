from GridPi import Core
from Assets import Models

import unittest

class TestCoreModule(unittest.TestCase):

    def setUp(self):
        self.test_system = Core.System()
        self.test_asset = Models.Asset()
        self.test_asset.config['name'] = 'test'

    def test_add_asset(self):
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