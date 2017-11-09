#!/usr/bin/env python3

from Core import TagBus, System
from Assets import Models
from Processes import Process

import HMI

import time
import logging

# Read system configuration
if __name__ == '__main__':

    """ Create Dummy Configs. These should be gathered from persistent storage once that system has been created.
    
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

    asset_cfgs = (feeder_config,
                  gridintertie_config,
                  energystorage_config) # a tuple containing asset configs

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

    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO) # configure logging

    """ ^^^ Everything above this line should be moved out of this script ^^^
    
    """

    """ Initalize System object.
    Create the system object. Load system assets, modules, and tagbus. Register the parameters of each asset with the
    tagbus object.
    
    """
    gp = System()                         # Create System container object

    """ Add Assets and Processes to System. The factory functions act on a dict that will eventually be held else
        where. The configuration property class_name is used to import the concrete asset or process.
    """

    asset_factory = Models.AssetFactory('Assets')  # Create Asset Factory object
    for cfg in asset_cfgs:
        gp.add_asset(asset_factory.factory(cfg))
    del asset_factory

    process_factory = Process.ProcessFactory('Processes')
    for cfg in process_cfgs:
        gp.add_process(process_factory.factory(cfg))
    del process_factory

    gp.register_tags() # System will register all Asset object parameters
    gp.process.sort(gp)

    """ Initalize HMI object
    
    """

    hmi = HMI.Application(gp) # Create HMI object

    """ System dispatch process loop
    
    """
    run = True
    while(run):
        gp.update_tagbus_from_assets()
        gp.run_processes()
        gp.write_assets_from_tagbus()

        try:
            hmi.update_tree(gp)
            hmi.update_idletasks()
            hmi.update()
        except:
            break

        time.sleep(.1)

    gp.tagbus.dump()