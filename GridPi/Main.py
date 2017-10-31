#!/usr/bin/env python3

from Core import TagBus, System
from Assets import Models
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
            "name": 'Feeder1',
            "cap_kw_pos_rated": 20,
            "cap_kw_neg_rated": 20,
            "cap_kvar_pos_rated": 20,
            "cap_kvar_neg_rated": 20,
        }
    }
    gridintertie_config = {
        'model_config': {
            "class_name": 'VirtualGridIntertie',
            "name": 'GridIntertie1',
            "cap_kw_pos_rated": 30,
            "cap_kw_neg_rated": 30,
            "cap_kvar_pos_rated": 15,
            "cap_kvar_neg_rated": 15,
        }
    }
    energystorage_config = {
        'model_config': {
            "class_name": 'VirtualEnergyStorage',
            "name": 'EnergyStorage1',
            "cap_kw_pos_rated": 20,
            "cap_kw_neg_rated": 20,
            "cap_kvar_pos_rated": 15,
            "cap_kvar_neg_rated": 15,
        }
    }

    asset_cfgs = (feeder_config, gridintertie_config, energystorage_config) # a tuple containing asset configs

    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG) # configure logging

    """ ^^^ Everything above this line should be moved out of this script ^^^
    
    """

    """ Initalize System object.
    Create the system object. Load system assets, modules, and tagbus. Register the parameters of each asset with the
    tagbus object.
    
    """
    gp = System()                         # Create System container object
    asset_factory = Models.AssetFactory('Assets') # Create Asset Factory object

    for cfg in asset_cfgs:                        # Add Assets to System, The asset factory acts on a configuration
        gp.add_asset(asset_factory.factory(cfg))  # dictionary file. using config_class_name to import the correct
                                                  # concrete asset class.

    del asset_factory # Delete the asset factory object, as it will not be used again.

    gp.register_tags()            # System will register all Asset object parameters with key 'status_*' as a
                                  # tag in system.Tagbus object.

    """ Initalize HMI object
    
    """

    hmi = HMI.Application(gp) # Create HMI object

    """ System dispatch process loop
    
    """
    while(True):
        gp.update_tagbus_from_assets()
#        gp.process_modules()
        gp.write_assets_from_tagbus()
        time.sleep(.05)
        try:
            hmi.update_idletasks()
            hmi.update()
        except:
            break