import unittest
import logging
import random

from GridPi import Core
from Models import Models
from Persistence import Persistence
from configparser import ConfigParser

class TestStorageClass(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)  # configure logging

        self.gp = Core.System()

        # configure asset models
        parser = ConfigParser()
        parser.read_dict({'FEEDER':
                                   {'class_name': 'VirtualFeeder',
                                    'name': 'feeder'},
                          'ENERGY_STORAGE':
                                   {'class_name': 'VirtualEnergyStorage',
                                    'name': 'inverter'},
                          'GRID_INTERTIE':
                                   {'class_name': 'VirtualGridIntertie',
                                    'name': 'grid'}})

        asset_factory = Models.AssetFactory()  # Create Asset Factory object
        for cfg in parser.sections():  # Add Models to System, The asset factory acts on a configuration
            self.gp.add_asset(asset_factory.factory(parser[cfg]))
        del asset_factory

        # configure persistence model
        parser.clear()
        parser.read_dict({'PERSISTENCE':
                              {'class_name': 'DBSQLite3',
                               'local_path': '/database/GridPi.sqlite',
                               'empty_database_on_start': 1}})
        persistence_factory = Persistence.PersistenceFactory()
        for cfg in parser.sections():
            self.db = persistence_factory.factory(parser[cfg])
        del persistence_factory

        self.gp.registerTags() # System will register all Asset object parameters

        asset_refs = [x for x in self.gp.assets]

        for asset in asset_refs:
            params = [p for p in asset.status.keys()]
            self.db.addGroup(asset.config['name'], *params)

    def tearDown(self):
        del self.gp
        del self.db

    def test_get_pid_names(self):
        for asset in self.gp.assets:
            # get all parameter_id's associated with feeder
            pid_tuple = self.db.get_pid_names(asset.config['name'])

            self.assertNotEqual(pid_tuple, {})
            self.assertIsNotNone(pid_tuple)

    def test_get_tag_pid_tuple(self):
        for asset in self.gp.assets:
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
        for asset in self.gp.assets:
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
            payload = self.db.packageTags(tag_pid_tuple, self.gp.read)

            self.assertNotEqual(payload, {})
            self.assertIsNotNone(payload)

    def test_write_payload(self):
        for asset in self.gp.assets:
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
            pkg = self.db.packageTags(tag_pid_tuple, self.gp.read)

            self.db.writeParam(payload=pkg)

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    unittest.main()