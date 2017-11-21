import unittest
import logging
import asyncio
import time

from GridPi import Core
from Assets import Models
from Processes import Process
from Storage import StorageInterface

import unittest

class TestGridPi(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)  # configure logging

        feeder_config = {
            'model_config': {
                "class_name": 'VirtualFeeder',
                "name": 'feeder',
                "cap_kw_pos_rated": 20,
                "cap_kw_neg_rated": 20,
            }
        }
        gridintertie_config = {
            'model_config': {
                "class_name": 'VirtualGridIntertie',
                "name": 'grid',
                "cap_kw_pos_rated": 30,
                "cap_kw_neg_rated": 30,
            }
        }
        energystorage_config = {
            'model_config': {
                "class_name": 'VirtualEnergyStorage',
                "name": 'inverter',
                "cap_kw_pos_rated": 20,
                "cap_kw_neg_rated": 20,
            }
        }

        # asset configs used to instantiate asset objects through the ProcessFactory object.
        asset_cfgs = (feeder_config,
                      gridintertie_config,
                      energystorage_config)  # a tuple containing asset configs

        inv_upt_status_config = {
            'model_config': {
                "class_name": 'INV_UPT_STATUS',
            }
        }
        grid_upt_status_config = {
            'model_config': {
                "class_name": 'GRID_UPT_STATUS',
            }
        }
        inv_soc_pwr_ctrl_config = {
            'model_config': {
                "class_name": 'INV_SOC_PWR_CTRL',
                "inverter_target_soc": 0.6
            }
        }
        inv_dmdlmt_pwr_ctrl_config = {
            'model_config': {
                "class_name": 'INV_DMDLMT_PWR_CTRL',
                "grid_kw_import_limit": 50,
                "grid_kw_export_limit": 50
            }
        }
        inv_wrt_ctrl_config = {
            'model_config': {
                "class_name": 'INV_WRT_CTRL'
            }
        }

        # process configs used to instantiate process objects through the ProcessFactory object.
        process_cfgs = (inv_upt_status_config,
                        grid_upt_status_config,
                        inv_soc_pwr_ctrl_config,
                        inv_dmdlmt_pwr_ctrl_config,
                        inv_wrt_ctrl_config)

        self.gp = Core.System()

        asset_factory = Models.AssetFactory('Assets')  # create AssetFactory object
        for cfg in asset_cfgs:
            self.gp.add_asset(asset_factory.factory(cfg))
        del asset_factory

        process_factory = Process.ProcessFactory('Processes') # create ProcessFactory object
        for cfg in process_cfgs:
            self.gp.add_process(process_factory.factory(cfg))
        del process_factory

        storage_factory = StorageInterface.StorageFactory('Storage')
        self.db = storage_factory.factory('DBSQLite3')

        self.gp.register_tags() # System will register all Asset object parameters
        self.gp.process.sort(self.gp)

    def test_async_asset_update(self):
        loop_update = asyncio.get_event_loop()
        for x in range(3):
            # Collect updateStatus() method references for each asset and package as coroutine task.
            tasks = asyncio.gather(*[x.updateStatus() for x in self.gp.assets.values()])
            loop_update.run_until_complete(tasks)
            time.sleep(1)

    def test_async_asset_write(self):
        loop_write = asyncio.get_event_loop()
        for x in range(3):
            # Collect updateStatus() method references for each asset and package as coroutine task.
            tasks = asyncio.gather(*[x.updateCtrl() for x in self.gp.assets.values()])
            loop_write.run_until_complete(tasks)
            time.sleep(1)
        loop_write.close()

if __name__ == '__main__':
    unittest.main()