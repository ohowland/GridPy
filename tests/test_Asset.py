#!/usr/bin/env python3

import unittest
import logging

from Assets import Models

class TestAssetModule(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

        self.energystorage_config = {
            'model_config': {
                "class_name": 'VirtualEnergyStorage',
                "name": 'inverter'
            }
        }

        self.test_asset = None

    def test_asset_factory(self):

        asset_factory = Models.AssetFactory('Assets')  # Create Asset Factory object
        self.test_asset = asset_factory.factory(self.energystorage_config)

    def test_virtual_state_machine(self):

        asset_factory = Models.AssetFactory('Assets')  # Create Asset Factory object
        self.test_asset = asset_factory.factory(self.energystorage_config)

        self.test_asset.updateStatus()

        self.test_asset.ctrl['run'] = True
        self.test_asset.updateCtrl()
        self.test_asset.updateStatus()

        self.assertEqual(self.test_asset.status['online'], True)

        self.test_asset.ctrl['run'] = False
        self.test_asset.updateCtrl()
        self.test_asset.updateStatus()

        self.assertEqual(self.test_asset.status['online'], False)

if __name__ == '__main__':
    unittest.main()