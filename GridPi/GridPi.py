"""GridPi acts as the software entry point.

"""

import Core, Models
from Assets.VirtualEnergyStorage import VirtualEnergyStorage
from Assets.VirtualFeeder import VirtualFeeder
from Assets.VirtualGridIntertie import VirtualGridIntertie

# Read system configuration
if __name__ == '__main__':

    feeder_config = {
        'model_config': {
            "process_name": 'Feeder1',
            "cap_kw_pos_rated": 20,
            "cap_kw_neg_rated": 20,
            "cap_kvar_pos_rated": 15,
            "cap_kvar_neg_rated": 15,
        }
    }

    gridintertie_config = {
        'model_config': {
            "process_name": 'GridIntertie1',
            "cap_kw_pos_rated": 20,
            "cap_kw_neg_rated": 20,
            "cap_kvar_pos_rated": 15,
            "cap_kvar_neg_rated": 15,
        }
    }

    energystorage_config = {
        'model_config': {
            "process_name": 'EnergyStorage1',
            "cap_kw_pos_rated": 20,
            "cap_kw_neg_rated": 20,
            "cap_kvar_pos_rated": 15,
            "cap_kvar_neg_rated": 15,
        }
    }

    # Initalize the System
    gp = Core.System()  # Create System container object

    gp.add_asset(VirtualGridIntertie(gridintertie_config))    # Add GridIntertie
    gp.add_asset(VirtualEnergyStorage(energystorage_config))  # Add EnergyStorage
    gp.add_asset(VirtualFeeder(feeder_config))                # Add Load Feeder

    gp.add_tagbus(Core.TagBus())  # Add Tagbus

    gp.register_tags()

