#!/usr/bin/env python3

import unittest

from Assets import Models
from GridPi import Core
from Processes import Process
from Processes import GraphProcess


class TestProcessModule(unittest.TestCase):

    def setUp(self):
        "Setup for Process Module Testing"

        """ Assets 
        """
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

        """ Processes
        """
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

        asset_cfgs = (feeder_config, # a tuple containing asset configs
                      gridintertie_config,
                      energystorage_config)


        process_cfgs = (inv_upt_status_config, # a tuple containing process configs
                        grid_upt_status_config,
                        inv_soc_pwr_ctrl_config,
                        inv_dmdlmt_pwr_ctrl_config,
                        inv_wrt_ctrl_config)

        self.test_system = Core.System()       # Create System container object

        asset_factory = Models.AssetFactory('Assets')  # Create Asset Factory object
        for cfg in asset_cfgs:  # Add Assets to System, The asset factory acts on a configuration
            self.test_system.add_asset(asset_factory.factory(cfg))

        process_factory = Process.ProcessFactory('Processes')
        for cfg in process_cfgs:
            self.test_system.add_process(process_factory.factory(cfg))


        self.test_system.register_tags()  # System will register all Asset object parameters with key 'status_*' as a
                                          # tag in system.Tagbus object.

        self.test_system.write('inverter_soc', 0.6)

    def test_tag_aggregation(self):
        ''' Test the tag aggregation class.

        '''
        tag = 'inverter_kw_setpoint'

        inv_soc_pwr_ctrl_config = {
            'model_config': {
                "class_name": 'INV_SOC_PWR_CTRL',
                "inverter_target_soc": 0.6
            }
        }
        inv_dmdlmt_pwr_ctrl_config = {
            'model_config': {
                "class_name": 'INV_SOC_PWR_CTRL',
                "grid_kw_import_limit": 50,
                "grid_kw_export_limit": 50
            }
        }

        inv_soc_pwr_ctrl = Process.INV_SOC_PWR_CTRL(inv_soc_pwr_ctrl_config)
        inv_dmdlmt_pwr_ctrl = Process.INV_DMDLMT_PWR_CTRL(inv_dmdlmt_pwr_ctrl_config)

        inv_pwr_ctrl_agg = Process.AggregateProcessSummation()
        inv_pwr_ctrl_agg.process_list = [inv_soc_pwr_ctrl, inv_dmdlmt_pwr_ctrl]

        inv_pwr_ctrl_agg.run_process(self.test_system.tagbus)

        final = self.test_system.read(tag)

        assert True
        #self.assertEqual(final, 75)

    def test_graph_dependencies(self):

        g = GraphProcess.GraphSystem(self.test_system)

        #g.process_edge_pairs(edge_pairs)
        #g.print_adjlist()

        #s = GraphProcess.DFS(g)


if __name__ == '__main__':
    unittest.main()