import logging
import time

from Assets import StateMachine
from Assets.Models import GridIntertie


class VirtualGridIntertie(GridIntertie):

    def __init__(self, config_dict):
        super(VirtualGridIntertie, self).__init__()

        self.internal_status.update({
            'kw': 0.0,
            'breaker_open': False,
            'breaker_trip': False
        })

        self.internal_ctrl.update({
            'close_breaker': False,
            'open_breaker': False
        })

        self.comm_interface = VGIDevice()  # Configure the communications interface (virtual component)
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

    async def updateCtrl(self):
        """ The update control routine on any asset is as follows:
            1. Map the abstract parent inferface to internal control dictionary
            2. Write the communications interface from internal control dictionary.
        """
        """ MAP TO INTERNAL HERE """
        self.internal_ctrl['close_breaker'] = self.ctrl['run']
        self.internal_ctrl['open_breaker'] = not self.ctrl['run']

        """ WRITE COMM INTERFACE """
        self.comm_interface.write(self.internal_ctrl)

class VGIDevice(StateMachine.StateMachine):
    def __init__(self):

        # Keep the persistent information about the device here.
        self.kw = 0.0
        self.breaker_open = True
        self.breaker_trip = False
        self.close_breaker = False
        self.open_breaker = False

        self.initialized = False
        self.looptime = time.time()

        StateMachine.StateMachine.__init__(self, state_initialize,  # Initialize State Machine
                                           Input(self.__dict__))

    def read(self, internal_status):
        """ Read state_machine_output class dict keys into internal_status
        """
        self.deviceUpdate()
        self.looptime = time.time()

        for key in internal_status.keys():
            internal_status[key] = self.__dict__[key]

    def write(self, internal_ctrl):
        """ Write internal_ctrl values to state_machine_input class dict keys
        """
        for key, val in internal_ctrl.items():
            self.__dict__[key] = val

        self.deviceUpdate()
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
        logging.debug('VirtualGridIntertie.StateMachine.State: Initialize')
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


class BreakerTripped(StateMachine.State):
    """ Startup state for the VES
    """
    def run(self, sm_input):
        logging.debug('VirtualGridIntertie.StateMachine.State: Tripped')
        sm_output = Output(dict())

        """ Breaker Trip Booleans """
        setattr(sm_output, 'breaker_open', True)

        """ Breaker kW Export """
        setattr(sm_output, 'kw', 0.0)

        logging.debug('VirtualGridIntertie.StateMachine.State output: %s', sm_output.__dict__)
        return sm_output

    def next(self, sm_input):
        if getattr(sm_input, 'open_breaker'):
            return state_open
        return state_tripped


class BreakerOpen(StateMachine.State):
    """ Offline state for the VES
    """
    def run(self, sm_input):
        logging.debug('VirtualGridIntertie.StateMachine.State: BreakerOpen')
        sm_output = Output(dict())  # create output msg object

        """ Breaker Trip Booleans """
        setattr(sm_output, 'breaker_trip', False)
        setattr(sm_output, 'breaker_open', True)

        """ Breaker kW Export """
        setattr(sm_output, 'kw', 0.0)

        logging.debug('VirtualGridIntertie.StateMachine.State output: %s', sm_output.__dict__)
        return sm_output

    def next(self, sm_input):
        if getattr(sm_input, 'breaker_trip'):
            return state_tripped
        if getattr(sm_input, 'close_breaker'): #and not getattr(sm_input, 'open_breaker'):
            return state_closed
        return state_open


class BreakerClosed(StateMachine.State):
    """ Online state for the VES
    """
    def run(self, sm_input):
        logging.debug('VirtualGridIntertie.StateMachine.State: BreakerClosed')
        sm_output = Output(dict())  # create output msg object

        """ Breaker Trip Booleans """
        setattr(sm_output, 'breaker_open', False)

        """ Breaker kW Export """
        setattr(sm_output, 'kw', 50.0)

        logging.debug('VirtualGridIntertie.StateMachine.State output: %s', sm_output.__dict__)
        return sm_output

    def next(self, sm_input):
        if getattr(sm_input, 'breaker_trip'):
            return state_tripped
        if not getattr(sm_input, 'close_breaker') and getattr(sm_input, 'open_breaker'):
            return state_open
        return state_closed

class Input(object):
    """ Input messaging object for the Virtual Energy Storage State Machine
    """
    def __init__(self, sm_input):
        self.__dict__.update(sm_input)

class Output(object):
    """ Output messaging object for the Virtual Energy Storage State Machine
    """
    def __init__(self, outpt):
        self.__dict__.update(outpt)

# Static variable initialization:
state_initialize = Initialize()
state_open = BreakerOpen()
state_closed = BreakerClosed()
state_tripped = BreakerTripped()
