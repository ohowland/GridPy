#!/usr/bin/env python3

import Core
from Models import Models
from Process import Process
from Persistence import Persistence
import HMI

import logging
import asyncio
from configparser import ConfigParser

# Read system configuration
if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)  # configure logging

    """ Initalize System object.
        Create the system object. Load system assets, modules, and tagbus. Register the parameters of each asset with the
        tagbus object.
    """
    gp = Core.System()  # Create System container object

    """ Add Models and Process to System. The factory functions act on a dict that will eventually be held else
        where. The configuration property class_name is used to import the concrete asset or process.
    """
    # read asset config.ini
    parser = ConfigParser()
    parser.read('asset_cfg.ini')
    asset_factory = Models.AssetFactory()  # Create Asset Factory object
    for cfg in parser.sections():
        gp.add_asset(asset_factory.factory(parser[cfg]))
    del asset_factory

    # read process config.ini
    parser.clear()
    parser.read('process_cfg.ini')
    process_factory = Process.ProcessFactory()
    for cfg in parser.sections():
        gp.add_process(process_factory.factory(parser[cfg]))
    del process_factory

    # read persistent storage config.ini
    parser.clear()
    parser.read('persistence_cfg.ini')
    persistence_factory = Persistence.PersistenceFactory()
    for cfg in parser.sections():
        db = persistence_factory.factory(parser[cfg])
    del persistence_factory

    gp.register_tags() # System will register all Asset object parameters
    gp.process.sort(gp)

    """ Initalize HMI object
    
    """

    hmi = HMI.Application(gp) # Create HMI object

    """ System dispatch process loop
    
    """

    loop = asyncio.get_event_loop()

    while(True):
        # Collect updateStatus() method references for each asset and package as coroutine task.
        update_asset_tasks = asyncio.gather(*[x.updateStatus() for x in gp.assets.values()])
        loop.run_until_complete(update_asset_tasks)

        # Push data from assets to the tagbus
        gp.update_tagbus_from_assets()

        # Run process
        gp.run_processes()

        # Push data from tagbus to assets
        gp.write_assets_from_tagbus()

        # Collect updateWrite() method references for each asset and package as coroutine task.
        write_asset_tasks = asyncio.gather(*[x.updateCtrl() for x in gp.assets.values()])
        loop.run_until_complete(write_asset_tasks)

        try:
            hmi.update_tree(gp)
            hmi.update_idletasks()
            hmi.update()
        except:
            break

    loop.close()
    gp.tagbus.dump()