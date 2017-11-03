import logging

from Assets.Models import Feeder


class VirtualFeeder(Feeder):

    def __init__(self, config_dict):
        super(VirtualFeeder, self).__init__()

        self.internal_status.update({
            'kw': 0.0,
            'breaker_open': False,
            'breaker_trip': False
        })

        self.internal_ctrl.update({
            'close_breaker': False,
            'open_breker': False
        })

        # self.internal_config.update({})

        self.initModel(config_dict)  # Write parameters in this model that match keys in the dictionary

        logging.debug('ASSET INTERFACE: %s constructed', self.config['name'])

    def __del__(self):
        logging.debug('ASSET INTERFACE: %s deconstructed', self.config['name'])

    async def updateStatus(self):
        """ The update status routine on any asset is as follows:
            1. Update internal dictionary from communications interface
            2. Map internal status dictionary to abstract parent interface
        """
        """ READ COMM INTERFACE """
        self.comm_interface.read(self.internal_status)

        """ MAP FROM INTERNAL HERE """
        self.status['kw'] = self.internal_status['kw']
        self.status['online'] = not self.internal_status['breaker_open']
        return

    async def updateControl(self):
        """ The update control routine on any asset is as follows:
            1. Map the abstract parent inferface to internal control dictionary
            2. Write the communications interface from internal control dictionary.
        """
        """ MAP TO INTERNAL HERE """
        self.internal_ctrl['close_breaker'] = self.ctrl['run'] and self.status['enabled']

        """ WRITE COMM INTERFACE """
        self.comm_interface.write(self.internal_ctrl)
        return
