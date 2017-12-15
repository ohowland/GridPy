import logging
import unittest
from configparser import ConfigParser

from GridPi.lib import gridpi_core
from GridPi.lib.models import model_core
from GridPi.lib.persistence import SQLAlchemyGP


class TestStorageClass(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)  # configure logging

        self.gp = gridpi_core.System()

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

        asset_factory = model_core.AssetFactory()  # Create Asset Factory object
        for cfg in parser.sections():  # Add models to System, The asset factory acts on a configuration
            self.gp.add_asset(asset_factory.factory(parser[cfg]))
        del asset_factory

        self.db = SQLAlchemyGP.SQLAlchemyGP()

    def tearDown(self):
        del self.gp
        del self.db

    def test_add_asset(self):

        for asset in self.gp.assets:
            self.db.add_asset(asset.config['name'])
            self.db.add_asset_params(asset.config['name'], 0, *list(asset.status.keys()))
            self.db.add_asset_params(asset.config['name'], 1, *list(asset.ctrl.keys()))

        self.db.session.commit()