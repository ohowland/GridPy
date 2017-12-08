#!/usr/bin/env python3

import Core
from Models import Models
from Process import Process
from Persistence import Persistence
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


async def update_persistent_storage(system, database, poll_rate):

    tag_list = list()
    for asset in system.assets:
        #database.connect()
        #group_id = database.addGroup(asset.config['name'])  # Add asset and params to relevent db tables

        database.add_asset(asset.config['name'])

        database.add_asset_params(asset.config['name'], 0, *list(asset.status.keys()))
        database.add_asset_params(asset.config['name'], 1, *list(asset.ctrl.keys()))

        #params = [p for p in asset.status.keys()]  # Get all params associated with asset
        #database.add_params_to_group(group_id, 'status', *params)
        #params = [p for p in asset.ctrl.keys()]  # Get all params associated with asset
        #database.add_params_to_group(group_id, 'control', *params)

        #param_status_info = database.get_pid_names(asset.config['name'], 'status')  # Retrieve all parameter IDs for params
        #param_ctrl_info = database.get_pid_names(asset.config['name'], 'control')
        #database.disconnect()

        #status_tag_pid_list = list()
        #for name, id in param_status_info:
        #    tag_name = ''.join(asset.config['name'] + '_' + name)
        #    status_tag_pid_list.append((tag_name, id))

        #status_pkg_list.append(tuple(status_tag_pid_list))


        #ctrl_tag_pid_list = list()
        #for name, id in param_ctrl_info:
        #    tag_name = ''.join(asset.config['name'] + '_' + name)
        #    ctrl_tag_pid_list.append((tag_name, id))

        #ctrl_pkg_list.append(tuple(ctrl_tag_pid_list))

        # TAG NAMES are of the form: asset_param
        status_tags = [asset.config['name'] + '_' + name for name in asset.status.keys()]
        ctrl_tags = [asset.config['name'] + '_' + name for name in asset.ctrl.keys()]

        tag_list += (status_tags)
        tag_list += (ctrl_tags)

    while True:
        print('[{time}] connecting to database'.format(time=datetime.now().time()))

        # TODO: this is inefficient, there is a better way to prepare the pkg tags.
        pkg = dict()
        for tag in tag_list:
            tagparts = tag.split('_')
            try:
                pkg[tagparts[0]].update({'_'.join(tagparts[1:]): system.read(tag)})
            except KeyError:
                pkg.update({tagparts[0]: {'_'.join(tagparts[1:]): system.read(tag)}})

        database.write_param(payload=pkg)
        print('[{time}] disconnecting from database'.format(time=datetime.now().time()))
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
    loop.create_task(update_persistent_storage(gp, db, 5))

    try:
        loop.run_forever()
    except:
        loop.close()
        gp.tagbus.dump()
