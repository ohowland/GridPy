""" Dispatch state machine templates and subclasses """

""" TEMPLATES: """
class State(object):
    def request(self, s_input):
        assert 0, "request not implemented"

    def transition(self, s_input, requested_state):
        assert 0, "transition not implemented"

    def action(self, requested_state):
        assert 0, "action not implemented"


class StateMachine(object):
    def __init__(self, initial_state):
        pass
        self.current_state = initial_state
        self.requested_state = self.current_state
        #self.current_state.action(sm_input)

    # Template method:
    def run(self, sm_input):
        self.requested_state = self.current_state.request(sm_input)
        self.current_state = self.current_state.transition(sm_input, self.requested_state)
        return self.current_state.action(self.requested_state)


class StateMachineMessage(object):
    def __init__(self):
        pass


""" SUBCLASSES: """
class DispatchStateMachine(StateMachine):
    def __init__(self, initial_state):
        super(DispatchStateMachine, self).__init__(initial_state)

    def run_all(self, asset_container):
        """ Run state_request, state_transition, and state_action
        """
        """ INSTANTIATE INPUT MSG """
        in_msg = self.current_state.input_msg(asset_container)

        """ RUN STATE """
        out_msg = self.run(in_msg)

        """ WRITE OUTPUT MSG TO ASSETS"""
        out_msg.write(asset_container)


class Blackout(State):
    def __init__(self):
        self.name = "Blackout State"
        self.input_msg = BlackoutInput
        self.output_msg = BlackoutOutput

    def request(self, inpt):
        """ Dispatch state request to state machine. Current State = Grid Connected
        """
        """ Transition Requests """
        if inpt.grid_enabled:
            return grid_state

        if inpt.ess_enabled:
            return ess_state

        """ No change in state requested """
        return blackout_state

    def transition(self, inpt, requested_state):
        """ Attempt to transition to requested state.
        """
        """ Transition Requests """
        if requested_state == grid_state:
            return grid_state

        if requested_state == ess_state:
            return ess_state

        """ No change in state """
        return blackout_state

    def action(self, requested_state):

        out = BlackoutOutput()

        out.feeder_run = True
        out.grid_run = False
        out.ess_run = False

        return out


class BlackoutInput(StateMachineMessage):
    def __init__(self, asset_container):
        super(BlackoutInput, self).__init__()

        grid = asset_container.get_asset('grid')[0]
        ess = asset_container.get_asset('ess')[0]

        self.grid_enabled = grid.status['enabled']
        self.ess_enabled = ess.status['enabled']


class BlackoutOutput(StateMachineMessage):
    def __init__(self):
        super(BlackoutOutput, self).__init__()

        self.grid_run = False
        self.ess_run = False
        self.feeder_run = False

    def write(self, asset_container):
        grid = asset_container.get_asset('grid')[0]
        grid.control['run'] = self.grid_run

        ess = asset_container.get_asset('ess')[0]
        ess.control['run'] = self.ess_run

        feeder = asset_container.get_asset('feeder')[0]
        feeder.control['run'] = self.feeder_run


class GridConnected(State):
    def __init__(self):
        self.name = "Grid Connected State"
        self.input_msg = GridConnectedInput
        self.output_msg = GridConnectedOutput

    def request(self, inpt):
        """ Dispatch state request to state machine. Current State = Grid Connected
        """
        """ Transition Requests """
        if not inpt.grid_enabled:
            if inpt.ess_online:  # Attempt transition to ESS grid forming.
                return ess_state

        """ No change in state requested """
        return grid_state

    def transition(self, inpt, requested_state):
        """ Attempt to transition to requested state.
        """
        """ Transition Requests """
        if requested_state == ess_state:
            return ess_state

        """ Emergency transitions """
        if not inpt.grid_enabled and inpt.ess_online:
            return ess_state

        """ No change in state """
        return grid_state

    def action(self, requested_state):

        out = GridConnectedOutput()

        out.ess_state_cmd = 1  # (0 = State.STANDBY, 1 = State.PQ, 2 = State.VF)
        out.feeder_run = True
        out.grid_run = True
        out.ess_run = True


        return out


class GridConnectedInput(StateMachineMessage):
    def __init__(self, asset_container):
        super(GridConnectedInput, self).__init__()

        grid = asset_container.get_asset('grid')[0]
        ess = asset_container.get_asset('ess')[0]

        self.grid_enabled = grid.status['enabled']
        self.ess_online = ess.status['online']
        #self.ess_enabled = ess.status['enabled']


class GridConnectedOutput(StateMachineMessage):
    def __init__(self):
        super(GridConnectedOutput, self).__init__()
        self.grid_run = False
        self.ess_run = False
        self.ess_state_cmd = 0
        self.feeder_run = False

    def write(self, asset_container):
        grid = asset_container.get_asset('grid')[0]
        grid.control['run'] = self.grid_run

        ess = asset_container.get_asset('ess')[0]
        ess.control['run'] = self.ess_run
        ess.control['state_cmd'] = self.ess_state_cmd

        feeder = asset_container.get_asset('feeder')[0]
        feeder.control['run'] = self.feeder_run


class ESSGridForming(State):
    def __init__(self):
        self.name = "ESS Grid Forming State"
        self.input_msg = ESSInput
        self.output_msg = ESSOutput

    def request(self, inpt):
        """ Dispatch state request to state machine. Current State = Grid Connected
        """
        """ Transition Requests """
        if inpt.grid_enabled:
            return grid_state

        """ No change in state requested """
        return ess_state

    def transition(self, inpt, requested_state):
        """ Attempt to transition to requested state.
        """
        """ Transition Requests """
        if requested_state == grid_state:
            return grid_state

        """ Emergency transitions """
        if not inpt.ess_enabled and inpt.grid_enabled:
            return grid_state

        """ No change in state """
        return ess_state

    def action(self, requested_state):

        out = ESSOutput()

        out.feeder_run = True
        out.ess_state_cmd = 2 # State.VF
        out.ess_run = True
        out.grid_run = False

        return out


class ESSInput(StateMachineMessage):
    def __init__(self, asset_container):
        super(ESSInput, self).__init__()

        grid = asset_container.get_asset('grid')[0]
        ess = asset_container.get_asset('ess')[0]

        self.grid_breaker_closed = grid.status['online']
        self.grid_enabled = grid.status['enabled']

        self.ess_online = ess.status['online']
        self.ess_alarm = ess.status['alarm']
        self.ess_enabled = ess.status['enabled']


class ESSOutput(StateMachineMessage):
    def __init__(self):
        super(ESSOutput, self).__init__()
        self.grid_run = False
        self.ess_run = False
        self.ess_state_cmd = 0
        self.feeder_run = False

    def write(self, asset_container):
        grid = asset_container.get_asset('grid')[0]
        grid.control['run'] = self.grid_run

        ess = asset_container.get_asset('ess')[0]
        ess.control['run'] = self.ess_run
        ess.control['state_cmd'] = self.ess_state_cmd

        feeder = asset_container.get_asset('feeder')[0]
        feeder.control['run'] = self.feeder_run


blackout_state = Blackout()
grid_state = GridConnected()
ess_state = ESSGridForming()

