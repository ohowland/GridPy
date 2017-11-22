#!/usr/bin/env python3

import unittest
import logging
import asyncio

from Models import Models
from Models import VirtualEnergyStorage
from Models import VirtualFeeder
from Models import VirtualGridIntertie
from configparser import ConfigParser

class TestModelModule(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

        self.parser = ConfigParser()
        self.parser.read_dict({'FEEDER':
                                   {'class_name': 'VirtualFeeder',
                                    'name': 'feeder'},
                               'ENERGY_STORAGE':
                                   {'class_name': 'VirtualEnergyStorage',
                                    'name': 'inverter'},
                               'GRID_INTERTIE':
                                   {'class_name': 'VirtualGridIntertie',
                                    'name': 'grid'}})
        self.test_asset = None
        self.loop = asyncio.get_event_loop()

    def tearDown(self):
        pass

    def test_asset_factory(self):
        logging.debug('********** Test Models asset factory **********')
        asset_factory = Models.AssetFactory()  # Create Asset Factory object

        self.test_asset = asset_factory.factory(self.parser['ENERGY_STORAGE'])
        self.assertIsInstance(self.test_asset, VirtualEnergyStorage.VirtualEnergyStorage)

        self.test_asset = asset_factory.factory(self.parser['FEEDER'])
        self.assertIsInstance(self.test_asset, VirtualFeeder.VirtualFeeder)

        self.test_asset = asset_factory.factory(self.parser['GRID_INTERTIE'])
        self.assertIsInstance(self.test_asset, VirtualGridIntertie.VirtualGridIntertie)

    def test_VES_state_machine(self):
        logging.debug('********** Test VirtualEnergyStorage state machine **********')
        asset_factory = Models.AssetFactory()  # Create Asset Factory object
        self.test_asset = asset_factory.factory(self.parser['ENERGY_STORAGE'])
        self.loop.run_until_complete(self.test_asset.updateStatus())

        kw_setpoint = 50.0
        self.test_asset.ctrl['run'] = True
        self.test_asset.ctrl['kw_setpoint'] = kw_setpoint
        self.loop.run_until_complete(self.test_asset.updateCtrl())
        self.loop.run_until_complete(self.test_asset.updateStatus())

        self.assertEqual(self.test_asset.status['online'], True)
        self.assertEqual(self.test_asset.status['kw'], kw_setpoint)

        self.test_asset.ctrl['run'] = False
        self.loop.run_until_complete(self.test_asset.updateCtrl())
        self.loop.run_until_complete(self.test_asset.updateStatus())

        self.assertEqual(self.test_asset.status['online'], False)
        self.assertEqual(self.test_asset.status['kw'], 0.0)

    def test_VES_state_machine_soc_tracking(self):
        logging.debug('********** Test VirtualEnergyStorage soc tracking **********')
        asset_factory = Models.AssetFactory()  # Create Asset Factory object
        self.test_asset = asset_factory.factory(self.parser['ENERGY_STORAGE'])  # Virtual Energy Persistence

        self.test_asset.ctrl['run'] = True
        self.test_asset.ctrl['kw_setpoint'] = 50.0
        self.loop.run_until_complete(self.test_asset.updateStatus())
        self.loop.run_until_complete(self.test_asset.updateCtrl())

        start_soc = self.test_asset.status['soc']
        for x in range(5):
            self.loop.run_until_complete(self.test_asset.updateStatus())

        self.assertLess(self.test_asset.status['soc'], start_soc)

    def test_VF_state_machine(self):
        logging.debug('********** Test VirtualFeeder state machine **********')
        asset_factory = Models.AssetFactory()  # Create Asset Factory object
        self.test_asset = asset_factory.factory(self.parser['FEEDER'])  # Virtual Feeder
        self.loop.run_until_complete(self.test_asset.updateStatus())

        self.test_asset.ctrl['run'] = True
        self.loop.run_until_complete(self.test_asset.updateCtrl())
        self.loop.run_until_complete(self.test_asset.updateStatus())

        self.assertEqual(self.test_asset.status['online'], True)

        self.test_asset.ctrl['run'] = False
        self.loop.run_until_complete(self.test_asset.updateStatus())
        self.loop.run_until_complete(self.test_asset.updateCtrl())

    def test_VGI_state_machine(self):
        logging.debug('********** Test VirtualGridIntertie state machine **********')

        asset_factory = Models.AssetFactory()  # Create Asset Factory object
        self.test_asset = asset_factory.factory(self.parser['GRID_INTERTIE'])  # Virtual GridIntertie
        self.loop.run_until_complete(self.test_asset.updateStatus())

        self.test_asset.ctrl['run'] = True
        self.loop.run_until_complete(self.test_asset.updateCtrl())
        self.loop.run_until_complete(self.test_asset.updateStatus())

        self.assertEqual(self.test_asset.status['online'], True)

        self.test_asset.ctrl['run'] = False
        self.loop.run_until_complete(self.test_asset.updateStatus())
        self.loop.run_until_complete(self.test_asset.updateCtrl())

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    unittest.main()