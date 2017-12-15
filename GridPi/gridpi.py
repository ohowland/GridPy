#!/usr/bin/env python3

import Core
from Models import model_core
from Process import process_core
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
            await asyncio.gather(*[asset.update_status() for asset in system.assets.assets]) #TODO: no assets.assets

            # Run calculate status processes
            print('[{time}] run process'.format(time=datetime.now().time()))
            system.run_processes()

            # Run the state macine
            print('[{time}] run state machine'.format(time=datetime.now().time()))
            system.state_machine.run()

            # Collect updateWrite() method references for each asset and package as coroutine task.
            print('[{time}] writing assets'.format(time=datetime.now().time()))
            await asyncio.gather(*[asset.update_control() for asset in system.assets.assets]) #TODO: no assets.assets

            await asyncio.sleep(poll_rate)

        except Exception as e:
            print(e, "-- Exiting GridPi")
            pending = asyncio.Task.all_tasks()
            for task in pending:
                task.cancel()
            asyncio.get_event_loop().stop()
            break


async def update_persistent_storage(system, database, poll_rate):

    status_payload = dict()
    ctrl_payload = dict()

    for asset in system.assets.assets:
        database.add_asset(asset.name)
        database.add_asset_params(asset.name, 0, *list(asset.__dict__.keys()))
        #database.add_asset_params(asset.name, 1, *['enable', 'run'])

        #status_payload.update({asset.name: dict()})
        #ctrl_payload.update({asset.config['name']: dict()})

        """payload: dict(AssetName: dict{param_name_1: value_1, ..., param_name_n, value_n}} """

        #status_payload[asset.name].update(asset.__dict__.items())
        #ctrl_payload[asset.config['name']].update(asset.ctrl.items())

    while True:
        #try:
            print('[{time}] connecting to database'.format(time=datetime.now().time()))

            """ Write database with Asset status information """
            status_payload = {}
            for asset in system.assets.assets:
                status_payload[asset.name] = {}
                for key, val in asset.__dict__.items():
                    status_payload[asset.name][key] = val
            print(status_payload)
            #database.write_param(payload=status_payload)

            """ Read Asset control information from database
            payload = database.read_param(payload=ctrl_payload)
            for asset, params in payload.items():
                for param, val in params.items():
                    system.write(asset + '_' + param, val)
            """

            print('[{time}] disconnecting from database'.format(time=datetime.now().time()))
            await asyncio.sleep(poll_rate)
        #except Exception as e:
        #    print('GP Database Loop Error: {error}'.format(error=e))
        #    break

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
    asset_factory = model_core.AssetFactory()  # Create Asset Factory object
    for cfg in parser.sections():
        gp.add_asset(asset_factory.factory(parser[cfg]))
    del asset_factory

    # read process config.ini
    parser.clear()
    parser.read(bootstrap_parser['BOOTSTRAP']['process_cfg_local_path'])
    process_factory = process_core.ProcessFactory()
    for cfg in parser.sections():
        gp.add_process(process_factory.factory(parser[cfg]))
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

    gp.process.sort()  # Sort the process tags by dependency

    loop = asyncio.get_event_loop()  # Get event loop
    loop.create_task(update_assets_loop(gp, poll_rate=.1))
    #loop.create_task(update_persistent_storage(gp, db, 5))

    try:
        loop.run_forever()
    except:
        loop.close()
