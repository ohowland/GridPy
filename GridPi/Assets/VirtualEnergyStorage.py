from Models import EnergyStorage
import logging

class VirtualEnergyStorage(EnergyStorage):

    def __init__(self, config_dict):
        EnergyStorage.__init__(self)

        self.init_model(config_dict)
        logging.debug('ASSET INTERFACE: %s constructed', self.config_process_name)

    def __del__(self):
        logging.debug('ASSET INTERFACE: %s deconstructed', self.config_process_name)

    def update(self):

        super(VirtualEnergyStorage, self).update()
