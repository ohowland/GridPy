import asyncio
import logging
import random
import time

from GridPi.lib.models import model_statemachine
from GridPi.lib.models.model_core import Feeder


class VirtualFeeder(Feeder):

    def __init__(self, config_dict, **kwargs):
        super(VirtualFeeder, self).__init__()

        self.internal_status.update({
            'kw': 0.0,
            'breaker_open': False,
            'breaker_trip': False
        })

        self.internal_control.update({
            'close_breaker': False,
            'open_breaker': False
        })

        self.comm_interface = VFDevice(**kwargs)  # Configure the communications interface (virtual component)
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
        await self.comm_interface.read(self.internal_status)

        """ MAP FROM INTERNAL HERE """
        self._status['kw'] = self.internal_status['kw']
        self._status['online'] = not self.internal_status['breaker_open']

        super(VirtualFeeder, self).update_status()

    async def update_control(self):
        """ The update control routine on any asset is as follows:
            1. Map the abstract parent inferface to internal control dictionary
            2. Write the communications interface from internal control dictionary.
        """
        super(VirtualFeeder, self).update_control()

        """ MAP TO INTERNAL HERE """
        self.internal_control['close_breaker'] = self._control['run'] and self._status['enabled']
        self.internal_control['open_breaker'] = not self._control['run'] or not self._status['enabled']

        """ WRITE COMM INTERFACE """
        await self.comm_interface.write(self.internal_control)

class VFDevice(model_statemachine.StateMachine):
    def __init__(self, **kwargs):

        # Keep the persistent information about the device here.
        self.kw = 0.0
        self.breaker_open = True
        self.breaker_trip = False
        self.close_breaker = False
        self.open_breaker = False

        self.initialized = False
        self.looptime = time.time()

        self.virtual_system = kwargs['virtual_system']

        model_statemachine.StateMachine.__init__(self, state_initialize,  # Initialize State Machine
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

        logging.debug('VirtualFeeder.StateMachine.state input: %s', internal_control)
        self.deviceUpdate()
        await asyncio.sleep(random.random())  # FUZZING
        self.looptime = time.time()

    def deviceUpdate(self):
        """ Run state machine, this would ideally go into a parallel loop.

        """
        sm_output = self.run(Input(self.__dict__))

        for key, val in sm_output.__dict__.items():
            setattr(self, key, val)

class Initialize(model_statemachine.State):
    """ Startup state for the VES
    """
    def run(self, sm_input):
        logging.debug('VirtualFeeder.StateMachine.State: Initialize')
        sm_output = Output(dict())

        """ Set Initialization Boolean """
        setattr(sm_output, 'initialized', True)

        return sm_output

    def next(self, sm_input):

        if getattr(sm_input, 'initialized'):
            if getattr(sm_input, 'breaker_trip'):
                return state_tripped
            if not getattr(sm_input, 'breaker_open'):
                return state_closed
            else:
                return state_open
        return state_initialize


class BreakerTripped(model_statemachine.State):
    """ Startup state for the VES
    """
    def run(self, sm_input):
        logging.debug('VirtualFeeder.StateMachine.State: Tripped')
        sm_output = Output(dict())

        """ Breaker Trip Booleans """
        setattr(sm_output, 'breaker_open', True)

        """ Breaker kW Export """
        setattr(sm_output, 'kw', 0.0)

        logging.debug('VirtualFeeder.StateMachine.State output: %s', sm_output.__dict__)
        return sm_output

    def next(self, sm_input):
        if getattr(sm_input, 'open_breaker'):
            return state_open
        return state_tripped


class BreakerOpen(model_statemachine.State):
    """ Offline state for the VES
    """
    def run(self, sm_input):
        logging.debug('VirtualFeeder.StateMachine.State: BreakerOpen')
        sm_output = Output(dict())  # create output msg object

        """ Breaker Trip Booleans """
        setattr(sm_output, 'breaker_trip', False)
        setattr(sm_output, 'breaker_open', True)

        """ Breaker kW Export """
        setattr(sm_output, 'kw', 0.0)

        logging.debug('VirtualFeeder.StateMachine.State output: %s', sm_output.__dict__)
        return sm_output

    def next(self, sm_input):
        if getattr(sm_input, 'breaker_trip'):
            return state_tripped
        if getattr(sm_input, 'close_breaker'): #and not getattr(sm_input, 'open_breaker'):
            return state_closed
        return state_open


class BreakerClosed(model_statemachine.State):
    """ Online state for the VES
    """
    def run(self, sm_input):
        logging.debug('VirtualFeeder.StateMachine.State: BreakerClosed')
        sm_output = Output(dict())  # create output msg object

        """ Breaker Trip Booleans """
        setattr(sm_output, 'breaker_open', False)

        """ Breaker kW Export """
        kw = getattr(sm_input, 'virtual_system').feeder_kw
        setattr(sm_output, 'kw', kw)  # pull value calculated in virtual system

        logging.debug('VirtualFeeder.StateMachine.State output: %s', sm_output.__dict__)
        return sm_output

    def next(self, sm_input):
        if getattr(sm_input, 'breaker_trip'):
            return state_tripped
        if not getattr(sm_input, 'close_breaker') and getattr(sm_input, 'open_breaker'):
            return state_open
        return state_closed


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
state_open = BreakerOpen()
state_closed = BreakerClosed()
state_tripped = BreakerTripped()