import asyncio
import logging
import random
import time

from GridPi.lib.models import model_statemachine
from GridPi.lib.models.model_core import EnergyStorage

class VirtualEnergyStorage(EnergyStorage):
    def __init__(self, config_dict, **kwargs):
        super(VirtualEnergyStorage, self).__init__()

        self.internal_status.update({
            'kw': 0.0,
            'online': False,
            'soc': 0.0
        })

        self.internal_control.update({
            'kw_setpoint': 0.0,
            'run_cmd': False,
            'state_cmd': EnergyStorage.State.STANDBY
        })

        self.comm_interface = VESDevice(**kwargs)  # Configure the communications interface (virtual component)
        self.read_config(config_dict)  # Write parameters in this model that match keys in the dictionary

        logging.debug('ASSET INTERFACE: %s constructed', self._config['name'])

    def __del__(self):
        logging.debug('ASSET INTERFACE: %s deconstructed', self._config['name'])

    async def update_status(self):
        """ The update status routine on any asset is as follows:
            1. Update internal dictionary from communications interface
            2. Map internal status dictionary to abstract parent interface
        """

        """ READ COMM INTERFACE """
        await self.comm_interface.read(self.internal_status)  # Performs device read and populates internal_status

        """ MAP from INTERNAL to ARCHETYPE """
        self._status['kw'] = self.internal_status['kw']
        self._status['online'] = self.internal_status['online']
        self._status['soc'] = self.internal_status['soc']

        super(VirtualEnergyStorage, self).update_status()

    async def update_control(self):
        """ The update control routine on any asset is as follows:
            1. Map the abstract parent interface to internal control dictionary
            2. Write the communications interface from internal control dictionary.
        """
        super(VirtualEnergyStorage, self).update_control()

        """ MAP from ARCHETYPE to INTERNAL """
        self.internal_control['kw_setpoint'] = self._control['kw_setpoint']
        self.internal_control['run_cmd'] = self._control['run'] and self._status['enabled']
        self.internal_control['state_cmd'] = self._control['state_cmd']

        """ WRITE COMM INTERFACE """
        await self.comm_interface.write(self.internal_control)


class VESDevice(model_statemachine.StateMachine):
    def __init__(self, **kwargs):

        # Keep the persistent information about the device here.
        self.kw = 0
        self.soc = 0.5
        self.kwh_capacity_rated = 30.0
        self.online = False
        self.run_cmd = False
        self.initialized = False
        self.kw_setpoint = 0
        self.looptime = time.time()
        self.state_cmd = EnergyStorage.State.STANDBY

        self.virtual_system = kwargs['virtual_system']

        model_statemachine.StateMachine.__init__(self, state_initialize,  # Initialize State Machine
                                                 Input(self.__dict__))

    async def read(self, internal_status):
        """ Read state_machine_output class dict keys into internal_status
        """

        self.device_update()
        await asyncio.sleep(random.random())  # FUZZING
        self.looptime = time.time()

        for key in internal_status.keys():
            internal_status[key] = self.__dict__[key]

    async def write(self, internal_control):
        """ Write internal_ctrl values to state_machine_input class dict keys
        """
        for key, val in internal_control.items():
            self.__dict__[key] = val

        logging.debug('VirtualEnergyStorage.StateMachine.state input: %s', internal_control)
        self.device_update()
        await asyncio.sleep(random.random())  # FUZZING
        self.looptime = time.time()

    def device_update(self):
        """ Run state machine, this would ideally go into a parallel loop.
        """
        sm_output = self.run(Input(self.__dict__))

        for key, val in sm_output.__dict__.items():
            setattr(self, key, val)


class Initialize(model_statemachine.State):
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


class Offline(model_statemachine.State):
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
            if getattr(sm_input, 'state_cmd') == EnergyStorage.State.VF.value:
                return state_onlineVF
            else:
                return state_onlinePQ
        return state_offline


class OnlinePQ(model_statemachine.State):
    """ Online state for the VES
    """

    def run(self, sm_input):
        logging.debug('VirtualEnergyStorage.StateMachine.State: Online - P/Q')
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

        """ Voltage / Frequency"""
        setattr(sm_output, 'volt')

        logging.debug('VirtualEnergyStorage.StateMachine.State output: %s', sm_output.__dict__)
        return sm_output

    def next(self, sm_input):
        if getattr(sm_input, 'run_cmd') == False:
            return state_offline
        if getattr(sm_input, 'state_cmd') == EnergyStorage.State.VF.value:
            return state_onlineVF
        return state_onlinePQ


class OnlineVF(model_statemachine.State):
    """ Online state for the VES
    """

    def run(self, sm_input):
        logging.debug('VirtualEnergyStorage.StateMachine.State: Online - V/F')
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
        # pull value calculated in virtual system
        kw = getattr(sm_input, 'virtual_system').ess_kw
        setattr(sm_output, 'kw', kw) # pull value calculated in virtual system

        logging.debug('VirtualEnergyStorage.StateMachine.State output: %s', sm_output.__dict__)
        return sm_output

    def next(self, sm_input):
        if getattr(sm_input, 'run_cmd') == False:
            return state_offline
        elif getattr(sm_input, 'state_cmd') == EnergyStorage.State.PQ.value:
            return state_onlinePQ
        return state_onlineVF


class Input(object):
    """ Input messaging object for the Virtual Energy persistence State Machine
    """

    def __init__(self, sm_input):
        self.__dict__.update(sm_input)


class Output(object):
    """ Output messaging object for the Virtual Energy persistence State Machine
    """

    def __init__(self, outpt):
        self.__dict__.update(outpt)


# Static variable initialization:
state_initialize = Initialize()
state_onlinePQ = OnlinePQ()
state_onlineVF = OnlineVF()
state_offline = Offline()
