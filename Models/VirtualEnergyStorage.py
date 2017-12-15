import logging
import time
import random
import asyncio

from Models import StateMachine

from Models.model_core import EnergyStorage

class VirtualEnergyStorage(EnergyStorage):

    def __init__(self, config_dict):
        super(VirtualEnergyStorage, self).__init__()

        self.internal_status.update({
            'kw': 0.0,
            'online': False,
            'soc': 0.0
        })

        self.internal_control.update({
            'kw_setpoint': 0.0,
            'run_cmd': False
        })

        self.comm_interface = VESDevice()  # Configure the communications interface (virtual component)
        self.initModel(config_dict)  # Write parameters in this model that match keys in the dictionary

        logging.debug('ASSET INTERFACE: %s constructed', self.config['name'])

    def __del__(self):
        logging.debug('ASSET INTERFACE: %s deconstructed', self.config['name'])

    async def update_status(self):
        """ The update status routine on any asset is as follows:
            1. Update internal dictionary from communications interface
            2. Map internal status dictionary to abstract parent interface
        """
        """ READ COMM INTERFACE """
        await self.comm_interface.read(self.internal_status)  # Performs device read and populates internal_status

        """ MAP from INTERNAL to ARCHETYPE """
        self.status['kw'] = self.internal_status['kw']
        self.status['online'] = self.internal_status['online']
        self.status['soc'] = self.internal_status['soc']

    async def update_control(self):
        """ The update control routine on any asset is as follows:
            1. Map the abstract parent inferface to internal control dictionary
            2. Write the communications interface from internal control dictionary.
        """
        """ MAP from ARCHETYPE to INTERNAL """
        self.internal_control['kw_setpoint'] = self.control['kw_setpoint']
        self.internal_control['run_cmd'] = self.control['run']

        """ WRITE COMM INTERFACE """
        await self.comm_interface.write(self.internal_control)


class VESDevice(StateMachine.StateMachine):
    def __init__(self):

        # Keep the persistent information about the device here.
        self.kw = 0
        self.soc = 0.5
        self.kwh_capacity_rated = 30.0
        self.online = False
        self.run_cmd = False
        self.initialized = False
        self.kw_setpoint = 0
        self.looptime = time.time()

        StateMachine.StateMachine.__init__(self, state_initialize,  # Initialize State Machine
                                           Input(self.__dict__))

    async def read(self, internal_status):
        """ Read state_machine_output class dict keys into internal_status
        """

        self.deviceUpdate()
        await asyncio.sleep(random.random())  # FUZZING
        self.looptime = time.time()

        for key in internal_status.keys():
            internal_status[key] = self.__dict__[key]

    async def write(self, internal_control):
        """ Write internal_ctrl values to state_machine_input class dict keys
        """
        for key, val in internal_control.items():
            self.__dict__[key] = val

        self.deviceUpdate()
        await asyncio.sleep(random.random())  # FUZZING
        self.looptime = time.time()

    def deviceUpdate(self):
        """ Run state machine, this would ideally go into a parallel loop.

        """
        sm_output = self.run(Input(self.__dict__))

        for key, val in sm_output.__dict__.items():
            setattr(self, key, val)

class Initialize(StateMachine.State):
    """ Startup state for the VES
    """
    def run(self, sm_input):
        logging.debug('VirtualEnergyStorage.StateMachine.State: Initialize')
        sm_output = Output(dict())

        setattr(sm_output, 'initialized', True)
        return sm_output

    def next(self, sm_input):

        if getattr(sm_input, 'initialized') == True:
            return state_offline
        return state_initialize


class Offline(StateMachine.State):
    """ Offline state for the VES
    """
    def run(self, sm_input):
        logging.debug('VirtualEnergyStorage.StateMachine.State: Offline')
        sm_output = Output(dict())  # create output msg object

        """ Calculate Online Status: """
        setattr(sm_output, 'online', False)

        """ Calculate SOC """
        soc = getattr(sm_input, 'soc')
        setattr(sm_output, 'soc', soc)

        """ Calculate kW output """
        setattr(sm_output, 'kw', 0.0)

        logging.debug('VirtualEnergyStorage.StateMachine.State output: %s', sm_output.__dict__)
        return sm_output

    def next(self, sm_input):
        if getattr(sm_input, 'run_cmd') == True:
            return state_online
        return state_offline


class Online(StateMachine.State):
    """ Online state for the VES
    """
    def run(self, sm_input):
        logging.debug('VirtualEnergyStorage.StateMachine.State: Online')
        sm_output = Output(dict())  # create output msg object

        """ Calculate Online Status: """
        setattr(sm_output, 'online', True)

        """ Calculate SOC """
        soc = getattr(sm_input, 'soc')
        kwh_rated = getattr(sm_input, 'kwh_capacity_rated')
        kw = getattr(sm_input, 'kw')
        looptime_hr = (time.time() - getattr(sm_input, 'looptime')) / 3600.0

        soc = (soc * kwh_rated - kw * looptime_hr) / kwh_rated
        setattr(sm_output, 'soc', soc)

        """ Calculate kW output """
        kw_setpoint = getattr(sm_input, 'kw_setpoint')
        setattr(sm_output, 'kw', kw_setpoint)

        logging.debug('VirtualEnergyStorage.StateMachine.State output: %s', sm_output.__dict__)
        return sm_output

    def next(self, sm_input):
        if getattr(sm_input, 'run_cmd') == False:
            return state_offline
        return state_online

class Input(object):
    """ Input messaging object for the Virtual Energy Persistence State Machine
    """
    def __init__(self, sm_input):
        self.__dict__.update(sm_input)

class Output(object):
    """ Output messaging object for the Virtual Energy Persistence State Machine
    """
    def __init__(self, outpt):
        self.__dict__.update(outpt)

# Static variable initialization:
state_initialize = Initialize()
state_online = Online()
state_offline = Offline()
