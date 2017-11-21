import unittest
import logging
import asyncio
import time
import sqlite3
import random

from GridPi import Core
from Assets import Models
from Storage import DBSQLite3

import unittest

class TestStorageClass(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)  # configure logging

        feeder_config = {
            'model_config': {
                "class_name": 'VirtualFeeder',
                "name": 'feeder',
                "cap_kw_pos_rated": 20,
                "cap_kw_neg_rated": 20,
            }
        }
        gridintertie_config = {
            'model_config': {
                "class_name": 'VirtualGridIntertie',
                "name": 'grid',
                "cap_kw_pos_rated": 30,
                "cap_kw_neg_rated": 30,
            }
        }
        energystorage_config = {
            'model_config': {
                "class_name": 'VirtualEnergyStorage',
                "name": 'inverter',
                "cap_kw_pos_rated": 20,
                "cap_kw_neg_rated": 20,
            }
        }

        asset_cfgs = (feeder_config,
                      gridintertie_config,
                      energystorage_config)  # a tuple containing asset configs

        self.gp = Core.System()

        asset_factory = Models.AssetFactory('Assets')  # Create Asset Factory object
        for cfg in asset_cfgs:
            self.gp.add_asset(asset_factory.factory(cfg))
        del asset_factory

        self.gp.register_tags() # System will register all Asset object parameters
        self.gp.process.sort(self.gp)

        self.db = DBSQLite3.DBSQLite3()

        asset_refs = [x for x in self.gp.assets.values()]

        for asset in asset_refs:
            params = [p for p in asset.status.keys()]
            self.db.addGroup(asset.config['name'], *params)

    def tearDown(self):
        del self.gp
        del self.db

    def test_get_pid_names(self):
        for asset in self.gp.assets.values():
            # get all parameter_id's associated with feeder
            pid_tuple = self.db.get_pid_names(asset.config['name'])

            self.assertNotEqual(pid_tuple, {})
            self.assertIsNotNone(pid_tuple)

    def test_get_tag_pid_tuple(self):
        for asset in self.gp.assets.values():
            # get all parameter_id's associated with a storage 'group' (in our case we group by asset name)
            name_pid_tuple = self.db.get_pid_names(asset.config['name'])

            # append the group name to the parameter name's (as 'groupName_paramName') found in the database.
            # together these form a Tagbus tag name.
            # TODO: where does this code belong? it interfaces the storage class with the Tagbus class.
            tag_pid_list = list()
            for param_name, pid in name_pid_tuple:
                tag_name = ''.join(asset.config['name'] + '_' + param_name)
                tag_pid_list.append((tag_name, pid))
            tag_pid_tuple = tuple(tag_pid_list)

            self.assertNotEqual(tag_pid_tuple, {})
            self.assertIsNotNone(tag_pid_tuple)

    def test_package_tags(self):
        for asset in self.gp.assets.values():
            # get all parameter_id's associated with a storage 'group' (in our case we group by asset name)
            name_pid_tuple = self.db.get_pid_names(asset.config['name'])

            # append the group name to the parameter name's (as 'groupName_paramName') found in the database.
            # together these form a Tagbus tag name.
            tag_pid_list = list()
            for param_name, pid in name_pid_tuple:
                tag_name = ''.join(asset.config['name'] + '_' + param_name) # tag name form: 'groupName_paramName'
                tag_pid_list.append((tag_name, pid))
            tag_pid_tuple = tuple(tag_pid_list)

            # create payload of parameter_ids and new current values.
            # give package_tags a reference to the gp.read function which accesses the tagbus data.
            payload = self.db.package_tags(tag_pid_tuple, self.gp.read)

            self.assertNotEqual(payload, {})
            self.assertIsNotNone(payload)

    def test_write_payload(self):
        for asset in self.gp.assets.values():
            # get all parameter_id's associated with a storage 'group' (in our case we group by asset name)
            name_pid_tuple = self.db.get_pid_names(asset.config['name'])

            # append the group name to the parameter name's (as 'groupName_paramName') found in the database.
            # together these form a Tagbus tag name.
            tag_pid_list = list()
            for param_name, pid in name_pid_tuple:
                tag_name = ''.join(asset.config['name'] + '_' + param_name) # tag name form: 'groupName_paramName'
                tag_pid_list.append((tag_name, pid))
            tag_pid_tuple = tuple(tag_pid_list)

            # use the tag names generated in the code above to access the Tagbus. write random values to these tags.
            for tag, _ in tag_pid_tuple:
                self.gp.write(tag, random.randint(0,1000))

            # create payload of parameter_ids and new current values.
            # give package_tags a reference to the gp.read function which accesses the tagbus data.
            pkg = self.db.package_tags(tag_pid_tuple, self.gp.read)

            self.db.writeParam(payload=pkg)