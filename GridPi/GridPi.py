"""GridPi acts as the software entry point.

1. Initialize Models
    a. Configure with data from sysconfig.json.
    b. Initialize communication abstraction
        I. Load abstraction for Model
.       II. Initialize modbus clients
            A. Instantiate object and launch thread.
            B. Tie Modbus client to a process.
2. Initialize Dispatch
    a. Configure with data from sysconfig.json
    b. Instantiate object
    c. Run

"""

import os
import json
import time
import Core, Models

# Read system configuration
if __name__ == '__main__':

    gp = Core.System()                      # Create System container object

    gp.add_asset(Models.GridIntertie())     # Add GridIntertie
    gp.add_asset(Models.EnergyStorage())    # Add EnergyStorage
    gp.add_asset(Models.Feeder())           # Add Load Feeder

    gp.add_tagbus(Core.TagBus())            # Add Tagbus

