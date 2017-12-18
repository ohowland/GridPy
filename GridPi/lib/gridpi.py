#!/usr/bin/env python3

import asyncio
import logging
from configparser import ConfigParser
from datetime import datetime
from collections import namedtuple

from GridPi.lib import gridpi_core
from GridPi.lib.models import model_core
from GridPi.lib.persistence import persistence_core
from GridPi.lib.process import process_core

async def update_assets_loop(system, poll_rate):

    while True:
        try:
            # Collect updateStatus() method references for each asset and package as coroutine task.
            print('[{time}] reading assets'.format(time=datetime.now().time()))
            await asyncio.gather(*[asset.update_status() for asset in system.asset_container.asset_list])

            # Run calculate status processes
            print('[{time}] run process'.format(time=datetime.now().time()))
            system.run_processes()

            # Run the state macine
            print('[{time}] run state machine'.format(time=datetime.now().time()))
            system.run_state_machine()
            print('[{time}] current state {state}'.format(time=datetime.now().time(),
                                                          state=system.state_machine.current_state.name))

            # Collect updateWrite() method references for each asset and package as coroutine task.
            print('[{time}] writing assets'.format(time=datetime.now().time()))
            await asyncio.gather(*[asset.update_control() for asset in system.asset_container.asset_list])
            await asyncio.sleep(poll_rate)

        except Exception as e:
            print(e, "*** Unrecoverable error, shutting down... ***")
            pending = asyncio.Task.all_tasks()
            for task in pending:
                task.cancel()
            asyncio.get_event_loop().stop()
            break


async def update_persistent_storage(system, database, poll_rate):

    status_payload = dict()
    status_pkg = dict()
    ctrl_payload = dict()
    pkg = namedtuple('pkg', 'asset, param_loc, param')

    for asset in system.asset_container.asset_list:
        database.add_asset(asset.config['class_type'])
        database.add_asset_params(asset.config['class_type'], 0, list(asset.status.keys()))
        database.add_asset_params(asset.config['class_type'], 1, list(asset.control.keys()))

        """payload: dict(AssetName: dict{param_name_1: value_1, ..., param_name_n, value_n}} """
        status_payload.update({asset.config['class_type']: dict()})
        status_payload[asset.config['class_type']].update(asset.status.items())

        ctrl_payload.update({asset.config['class_type']: dict()})
        ctrl_payload[asset.config['class_type']].update(asset.control.items())

    while True:
        try:
            print('[{time}] connecting to database'.format(time=datetime.now().time()))

            """ Write database with Asset status information """
            for asset in system.asset_container.asset_list:
                status_payload[asset.config['class_type']].update(asset.status.items())
                database.write_param(payload=status_payload)

            """ Read Asset control information from database """

            payload = database.read_param(payload=ctrl_payload)
            for asset, params in payload.items():
                local_asset = system.asset_container.get_asset(asset)[0]
                for param, val in params.items():
                    local_asset.control[param] = val

            print('[{time}] disconnecting from database'.format(time=datetime.now().time()))
            await asyncio.sleep(poll_rate)
        except Exception as e:
            print('GP Database Loop Error: {error}'.format(error=e))
            break

def main(*args, **kwargs):
    """ Initalize System object.
        Create the system object. Load system assets, modules, and tagbus. Register the parameters of each asset with the
        tagbus object.
    """
    gp = gridpi_core.System()  # Create System container object


    # read asset config.ini
    bootstrap_parser = kwargs['bootstrap']
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
    persistence_factory = persistence_core.PersistenceFactory()
    for cfg in parser.sections():
        db = persistence_factory.factory(parser[cfg])
    del persistence_factory
    del bootstrap_parser
    del parser

    gp.process_container.sort()  # Sort the process tags by dependency

    loop = asyncio.get_event_loop()  # Get event loop
    loop.create_task(update_assets_loop(gp, poll_rate=.1))
    loop.create_task(update_persistent_storage(gp, db, 5))

    try:
        loop.run_forever()
    except:
        loop.close()
