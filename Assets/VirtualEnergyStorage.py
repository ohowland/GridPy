import logging

from Assets.Models import EnergyStorage


class VirtualEnergyStorage(EnergyStorage):

    def __init__(self, config_dict):
        super(VirtualEnergyStorage, self).__init__()

        self.internal_status.update({
            'kw': 0.0,
            'online': False,
            'soc': 0.0
        })

        self.internal_ctrl.update({
            'kw_setpoint': 0.0,
            'run_cmd': False
        })

        self.comm_interface = VirtualEnergyStorageStateMachine()

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
        self.comm_interface.read(self.internal_status)  #  Performs device read and populates internal_status

        """ MAP FROM INTERNAL HERE """
        self.status['kw'] = self.internal_status['kw']
        self.status['online'] = self.internal_status['online']
        return

    async def updateControl(self):
        """ The update control routine on any asset is as follows:
            1. Map the abstract parent inferface to internal control dictionary
            2. Write the communications interface from internal control dictionary.
        """
        """ MAP TO INTERNAL HERE """
        self.internal_ctrl['kw_setpoint'] = self.ctrl['kw_setpoint']
        self.internal_ctrl['run_cmd'] = self.ctrl['run'] and self.status['enabled']

        """ WRITE COMM INTERFACE """
        self.comm_interface.write(self.internal_ctrl)
        return

class VirtualEnergyStorageStateMachine(object):
    def __init__(self):

        self.kw = 0.0
        self.online = False
        self.soc = 0.6
        self.rated_kw = 100.0
        self.rated_kwh = 20.0

        self.kw_setpoint = 0.0
        self.run = False

    def read(self, internal_status):

        internal_status['kw'] = self.kw_setpoint
        internal_status['online'] = self.run
        internal_status['soc'] = self.soc

    def write(self, internal_control):

        self.kw_setpoint = internal_control['kw_setpoint']
        self.run = internal_control['run_cmd']