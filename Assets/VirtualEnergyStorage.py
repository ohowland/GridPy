import logging

from Assets.Models import EnergyStorage


class VirtualEnergyStorage(EnergyStorage):

    def __init__(self, config_dict):
        super(VirtualEnergyStorage, self).__init__()

        self.init_model(config_dict)
        logging.debug('ASSET INTERFACE: %s constructed', self.config['name'])

    def __del__(self):
        logging.debug('ASSET INTERFACE: %s deconstructed', self.config['name'])

    def update(self):

        super(VirtualEnergyStorage, self).update()
