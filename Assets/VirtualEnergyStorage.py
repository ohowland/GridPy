import logging
from Assets import StateMachine

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

        self.comm_interface = VESDevice(self.internal_status, self.internal_ctrl)  # Configure the communications interface (virtual component)
        self.initModel(config_dict)  # Write parameters in this model that match keys in the dictionary

        logging.debug('ASSET INTERFACE: %s constructed', self.config['name'])

    def __del__(self):
        logging.debug('ASSET INTERFACE: %s deconstructed', self.config['name'])

    def updateStatus(self):
        """ The update status routine on any asset is as follows:
            1. Update internal dictionary from communications interface
            2. Map internal status dictionary to abstract parent interface
        """
        """ READ COMM INTERFACE """
        self.comm_interface.read(self.internal_status)  # Performs device read and populates internal_status

        """ MAP from INTERNAL to ARCHETYPE """
        self.status['kw'] = self.internal_status['kw']
        self.status['online'] = self.internal_status['online']
        self.status['soc'] = self.internal_status['soc']
        return

    def updateCtrl(self):
        """ The update control routine on any asset is as follows:
            1. Map the abstract parent inferface to internal control dictionary
            2. Write the communications interface from internal control dictionary.
        """
        """ MAP from ARCHETYPE to INTERNAL """
        self.internal_ctrl['kw_setpoint'] = self.ctrl['kw_setpoint']
        self.internal_ctrl['run_cmd'] = self.ctrl['run']

        """ WRITE COMM INTERFACE """
        self.comm_interface.write(self.internal_ctrl)
        return


class VESDevice(StateMachine.StateMachine):
    def __init__(self, internal_status, internal_ctrl):

        self.state_machine_input = Input(internal_ctrl)          # State machine input message object
        self.state_machine_output = Output(internal_status)      # State machine output message object
        StateMachine.StateMachine.__init__(self, state_offline,  # Initialize State Machine
                                           self.state_machine_input,
                                           self.state_machine_output)

    def read(self, internal_status):
        """ Read state_machine_output class dict keys into internal_status
        """
        self.deviceUpdate()
        for key in internal_status.keys():
            internal_status[key] = self.state_machine_output.__dict__[key]

    def write(self, internal_ctrl):
        """ Write internal_ctrl values to state_machine_input class dict keys
        """
        self.deviceUpdate()
        for key, val in internal_ctrl.items():
            self.state_machine_input.__dict__[key] = val

    def deviceUpdate(self):
        self.state_machine_output = self.run(self.state_machine_input, self.state_machine_output)


class Offline(StateMachine.State):
    def run(self, smInput, smOutput):
        logging.debug('VirtualEnergyStorage.StateMachine(): STATE: Offline')

        setattr(smOutput, 'online', False)
        logging.debug('VirtualEnergyStorage.StateMachine.State output: %s', smOutput.__dict__)
        return smOutput

    def next(self, smInput):
        if getattr(smInput, 'run_cmd') == True:
            return state_online
        return state_offline


class Online(StateMachine.State):
    def run(self, smInput, smOutput):
        logging.debug('VirtualEnergyStorage.StateMachine(): STATE: Online')

        setattr(smOutput, 'online', True)
        return smOutput

    def next(self, smInput):
        if getattr(smInput, 'run_cmd') == False:
            return state_offline
        return state_online

class Input(object):
    """ Input messaging object for the Virtual Energy Storage State Machine
    """
    def __init__(self, msg):
        self.__dict__.update(msg)

    def __cmp__(self, other):
        return self.__dict__ == other.__dict__

class Output(object):
    """ Output messaging object for the Virtual Energy Storage State Machine
    """
    def __init__(self, msg):
        self.__dict__.update(msg)

# Static variable initialization:
state_online = Online()
state_offline = Offline()
