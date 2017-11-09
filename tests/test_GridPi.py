import unittest
import logging

from GridPi import Core
from Assets import Models
from Processes import Process

import unittest

class TestGridPi(unittest.TestCase):

    def setUp(self):

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

        process_cfgs = (inv_upt_status_config,  # a tuple containing process configs
                        grid_upt_status_config,
                        inv_soc_pwr_ctrl_config,
                        inv_dmdlmt_pwr_ctrl_config,
                        inv_wrt_ctrl_config)

        self.gp = Core.System()

        asset_factory = Models.AssetFactory('Assets')  # Create Asset Factory object
        for cfg in asset_cfgs:
            self.gp.add_asset(asset_factory.factory(cfg))
        del asset_factory

        process_factory = Process.ProcessFactory('Processes')
        for cfg in process_cfgs:
            self.gp.add_process(process_factory.factory(cfg))
        del process_factory

        self.gp.register_tags() # System will register all Asset object parameters
        self.gp.process.sort(self.gp)

if __name__ == '__main__':
    unittest.main()