import logging

from Assets.Models import Feeder


class VirtualFeeder(Feeder):

    def __init__(self, config_dict):
        super(VirtualFeeder, self).__init__()

        self.init_model(config_dict)
        logging.debug('ASSET INTERFACE: %s constructed', self.config['name'])

    def __del__(self):
        logging.debug('ASSET INTERFACE: %s deconstructed', self.config['name'])

    def update(self):

        super(VirtualFeeder, self).update()
