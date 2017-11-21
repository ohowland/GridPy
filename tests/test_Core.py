from GridPi import Core
from Assets import Models

import unittest

class TestCoreModule(unittest.TestCase):

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

        self.asset_cfgs = (feeder_config,
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

        self.process_cfgs = (inv_upt_status_config,  # a tuple containing process configs
                        grid_upt_status_config,
                        inv_soc_pwr_ctrl_config,
                        inv_dmdlmt_pwr_ctrl_config,
                        inv_wrt_ctrl_config)

        self.test_system = Core.System()
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