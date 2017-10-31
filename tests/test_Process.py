#!/usr/bin/env python3

import unittest

from Assets import Models
from GridPi import Core
from Processes import Process


class TestProcessModule(unittest.TestCase):

    def setUp(self):

        feeder_config = {
            'model_config': {
                "class_name": 'VirtualFeeder',
                "name": 'feeder',
                "cap_kw_pos_rated": 20,
                "cap_kw_neg_rated": 20,
                "cap_kvar_pos_rated": 20,
                "cap_kvar_neg_rated": 20,
            }
        }
        gridintertie_config = {
            'model_config': {
                "class_name": 'VirtualGridIntertie',
                "name": 'grid',
                "cap_kw_pos_rated": 30,
                "cap_kw_neg_rated": 30,
                "cap_kvar_pos_rated": 15,
                "cap_kvar_neg_rated": 15,
            }
        }
        energystorage_config = {
            'model_config': {
                "class_name": 'VirtualEnergyStorage',
                "name": 'inverter',
                "cap_kw_pos_rated": 20,
                "cap_kw_neg_rated": 20,
                "cap_kvar_pos_rated": 15,
                "cap_kvar_neg_rated": 15,
            }
        }

        asset_cfgs = (feeder_config, gridintertie_config, energystorage_config)  # a tuple containing asset configs

        self.test_system = Core.System()       # Create System container object
        asset_factory = Models.AssetFactory('Assets')  # Create Asset Factory object

        for cfg in asset_cfgs:  # Add Assets to System, The asset factory acts on a configuration
            self.test_system.add_asset(asset_factory.factory(cfg))

        self.test_system.register_tags()  # System will register all Asset object parameters with key 'status_*' as a
                                          # tag in system.Tagbus object.

    def test_tag_aggregation(self):
        ''' Test the tag aggregation class.

        '''
        tag = 'inverter_kw_setpoint'
        print(tag, 'tag pre-process:', self.test_system.read(tag))

        inv_soc_pwr_ctrl = Process.INV_SOC_PWR_CTRL()
        inv_dmdlmt_pwr_ctrl = Process.INV_DMDLMT_PWR_CTRL()

        inv_pwr_ctrl_agg = Process.AggregateProcessSummation()
        inv_pwr_ctrl_agg.process_list = [inv_soc_pwr_ctrl, inv_dmdlmt_pwr_ctrl]

        inv_pwr_ctrl_agg.run_process(self.test_system.tagbus)

        final = self.test_system.read(tag)
        print(tag, 'tag post-process:', final)

        self.assertEqual(final, 75)

if __name__ == '__main__':
    unittest.main()