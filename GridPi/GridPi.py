#!/usr/bin/env python3

import Core
from Models import Models
from Process import Process
from Persistence import Persistence
import HMI
import signal

import logging
import asyncio
from configparser import ConfigParser
from pathlib import Path

# Read system configuration
async def update_assets_loop(system, poll_rate):
    while True:
        try:
            # Collect updateStatus() method references for each asset and package as coroutine task.
            print('reading assets...')
            await asyncio.gather(*[asset.updateStatus() for asset in gp.assets])

            # Push data from assets to the tagbus
            system.updateTagbusFromAssets()

            # Run process
            print('run process...')
            system.runProcesses()

            # Push data from tagbus to assets
            system.writeAssetsFromTagbus()

            # Collect updateWrite() method references for each asset and package as coroutine task.
            print('writing assets...')
            await asyncio.gather(*[asset.updateCtrl() for asset in gp.assets])

            await asyncio.sleep(poll_rate)

        except KeyboardInterrupt:
            asyncio.get_event_loop().stop()
            break

async def update_hmi(gp, poll_rate):
    hmi = HMI.Application(gp)  # Create HMI object
    while True:
        try:
            hmi.update_tree(gp)
            hmi.update_idletasks()
            hmi.update()
            await asyncio.sleep(poll_rate)
        except:
            asyncio.get_event_loop().stop()
            break


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)  # configure logging

    """ Initalize System object.
        Create the system object. Load system assets, modules, and tagbus. Register the parameters of each asset with the
        tagbus object.
    """
    gp = Core.System()  # Create System container object

    bootstrap_parser = ConfigParser()
    bootstrap_parser.read('config/bootstrap.ini')

    # read asset config.ini
    parser = ConfigParser()
    parser.read(bootstrap_parser['BOOTSTRAP']['asset_cfg_local_path'])
    asset_factory = Models.AssetFactory()  # Create Asset Factory object
    for cfg in parser.sections():
        gp.addAsset(asset_factory.factory(parser[cfg]))
    del asset_factory

    # read process config.ini
    parser.clear()
    parser.read(bootstrap_parser['BOOTSTRAP']['process_cfg_local_path'])
    process_factory = Process.ProcessFactory()
    for cfg in parser.sections():
        gp.addProcess(process_factory.factory(parser[cfg]))
    del process_factory

    # read persistent storage config.ini
    parser.clear()
    parser.read(bootstrap_parser['BOOTSTRAP']['persistence_cfg_local_path'])
    persistence_factory = Persistence.PersistenceFactory()
    for cfg in parser.sections():
        db = persistence_factory.factory(parser[cfg])
    del persistence_factory
    del bootstrap_parser
    del parser

    gp.registerTags()  # System will register all Asset object parameters
    gp.process.sort()  # Sort the process tags by dependency



    loop = asyncio.get_event_loop() # Get event loop
    loop.create_task(update_assets_loop(gp, poll_rate=1))
    loop.create_task(update_hmi(gp, .2))
    try:
        loop.run_forever()
    except:
        loop.close()
        gp.tagbus.dump()