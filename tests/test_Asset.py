#!/usr/bin/env python3

import unittest
import logging
import time

from Assets import Models
from Assets import VirtualEnergyStorage
from Assets import VirtualFeeder
from Assets import VirtualGridIntertie

class TestAssetModule(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

        self.energystorage_config = {
            'model_config': {
                "class_name": 'VirtualEnergyStorage',
                "name": 'inverter'
            }
        }

        self.feeder_config = {
            'model_config': {
                "class_name": 'VirtualFeeder',
                "name": 'feeder'
            }
        }

        self.grid_config = {
            'model_config': {
                "class_name": 'VirtualGridIntertie',
                "name": 'grid'
            }
        }

        self.test_asset = None

    def test_asset_factory(self):
        logging.debug('********** Test Models asset factory **********')
        asset_factory = Models.AssetFactory('Assets')  # Create Asset Factory object

        self.test_asset = asset_factory.factory(self.energystorage_config)
        self.assertIsInstance(self.test_asset, VirtualEnergyStorage.VirtualEnergyStorage)

        self.test_asset = asset_factory.factory(self.feeder_config)
        self.assertIsInstance(self.test_asset, VirtualFeeder.VirtualFeeder)

        self.test_asset = asset_factory.factory(self.grid_config)
        self.assertIsInstance(self.test_asset, VirtualGridIntertie.VirtualGridIntertie)

    def test_VES_state_machine_(self):
        logging.debug('********** Test VirtualEnergyStorage state machine **********')
        asset_factory = Models.AssetFactory('Assets')  # Create Asset Factory object
        self.test_asset = asset_factory.factory(self.energystorage_config)
        self.test_asset.updateStatus()

        kw_setpoint = 50.0
        self.test_asset.ctrl['run'] = True
        self.test_asset.ctrl['kw_setpoint'] = kw_setpoint
        self.test_asset.updateCtrl()
        self.test_asset.updateStatus()

        self.assertEqual(self.test_asset.status['online'], True)
        self.assertEqual(self.test_asset.status['kw'], kw_setpoint)

        self.test_asset.ctrl['run'] = False
        self.test_asset.updateCtrl()
        self.test_asset.updateStatus()

        self.assertEqual(self.test_asset.status['online'], False)
        self.assertEqual(self.test_asset.status['kw'], 0.0)

    def test_VES_state_machine_kwh(self):
        logging.debug('********** Test VirtualEnergyStorage soc tracking **********')
        asset_factory = Models.AssetFactory('Assets')  # Create Asset Factory object
        self.test_asset = asset_factory.factory(self.energystorage_config)  # Virtual Energy Storage

        self.test_asset.ctrl['run'] = True
        self.test_asset.ctrl['kw_setpoint'] = 50.0
        self.test_asset.updateStatus()
        self.test_asset.updateCtrl()

        start_soc = self.test_asset.status['soc']
        for x in range(5):
            self.test_asset.updateStatus()
            time.sleep(.1)

        self.assertLess(self.test_asset.status['soc'], start_soc)

    def test_VF_state_machine_(self):
        logging.debug('********** Test VirtualFeeder state machine **********')
        asset_factory = Models.AssetFactory('Assets')  # Create Asset Factory object
        self.test_asset = asset_factory.factory(self.feeder_config)  # Virtual Feeder
        self.test_asset.updateStatus()

        self.test_asset.ctrl['run'] = True
        self.test_asset.updateCtrl()
        self.test_asset.updateStatus()

        self.assertEqual(self.test_asset.status['online'], True)

        self.test_asset.ctrl['run'] = False
        self.test_asset.updateStatus()
        self.test_asset.updateCtrl()

    def test_VGI_state_machine_(self):
        logging.debug('********** Test VirtualGridIntertie state machine **********')

        asset_factory = Models.AssetFactory('Assets')  # Create Asset Factory object
        self.test_asset = asset_factory.factory(self.grid_config)  # Virtual GridIntertie
        self.test_asset.updateStatus()

        self.test_asset.ctrl['run'] = True
        self.test_asset.updateCtrl()
        self.test_asset.updateStatus()

        self.assertEqual(self.test_asset.status['online'], True)

        self.test_asset.ctrl['run'] = False
        self.test_asset.updateStatus()
        self.test_asset.updateCtrl()



if __name__ == '__main__':
    unittest.main()