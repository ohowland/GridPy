#!/usr/bin/env python3

import Core
from Models import Models
from Process import Process
from Persistence import Persistence
import HMI
from datetime import datetime

import logging
import asyncio
from configparser import ConfigParser


async def update_assets_loop(system, poll_rate):
    while True:
        try:
            # Collect updateStatus() method references for each asset and package as coroutine task.
            print('[{time}] reading assets'.format(time=datetime.now().time()))
            await asyncio.gather(*[asset.updateStatus() for asset in gp.assets])

            # Push data from assets to the tagbus
            system.updateTagbusFromAssets()

            # Run process
            print('[{time}] run process'.format(time=datetime.now().time()))
            system.runProcesses()

            # Push data from tagbus to assets
            system.writeAssetsFromTagbus()

            # Collect updateWrite() method references for each asset and package as coroutine task.
            print('[{time}] writing assets'.format(time=datetime.now().time()))
            await asyncio.gather(*[asset.updateCtrl() for asset in gp.assets])

            await asyncio.sleep(poll_rate)

        except KeyboardInterrupt:
            asyncio.get_event_loop().stop()
            break


async def update_hmi(system, poll_rate):
    hmi = HMI.Application(system)  # Create HMI object
    while True:
        try:
            hmi.update_tree(system)
            await asyncio.sleep(poll_rate)
        except:
            asyncio.get_event_loop().stop()
            break


async def update_persistent_storage(system, database, poll_rate):

    pkg_list = list()
    for asset in system.assets:
        params = [p for p in asset.status.keys()]         # Get all params associated with asset
        database.addGroup(asset.config['name'], *params)  # Add asset and params to relevent db tables

        param_info = database.get_pid_names(asset.config['name'])  # Retrieve all parameter IDs for params
        tag_pid_list = list()
        for name, id in param_info:
            tag_name = ''.join(asset.config['name'] + '_' + name)
            tag_pid_list.append((tag_name, id))

        pkg_list.append(tuple(tag_pid_list))

    while True:
        print('[{time}] writing database'.format(time=datetime.now().time()))
        for tag_set in pkg_list:
            pkg = database.packageTags(tag_set, system.read)
            database.writeParam(payload=pkg)
        await asyncio.sleep(poll_rate)


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)  # configure logging

    """ Initalize System object.
        Create the system object. Load system assets, modules, and tagbus. Register the parameters of each asset with the
        tagbus object.
    """
    gp = Core.System()  # Create System container object

    # Read system configuration
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

    loop = asyncio.get_event_loop()  # Get event loop
    loop.create_task(update_assets_loop(gp, poll_rate=.1))
    loop.create_task(update_hmi(gp, .2))
    loop.create_task(update_persistent_storage(gp, db, 5))

    try:
        loop.run_forever()
    except:
        loop.close()
        gp.tagbus.dump()
