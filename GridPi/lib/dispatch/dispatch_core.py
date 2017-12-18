""" Dispatch state machine templates and subclasses """

""" TEMPLATES: """
class State(object):
    def request(self, s_input):
        assert 0, "request not implemented"

    def action(self, s_input, requested_state):
        assert 0, "action not implemented"

    def transition(self, s_input, requested_state):
        assert 0, "transition not implemented"


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
        return self.current_state.action(sm_input, self.requested_state)


class StateMachineMessage(object):
    def __init__(self, asset_container):
        pass

""" SUBCLASSES: """
class DispatchStateMachine(StateMachine):
    def __init__(self, initial_state):
        super(DispatchStateMachine, self).__init__(initial_state)

    def run_all(self, asset_container):

        if self.current_state == blackout_state:
            msg = BlackoutInput(asset_container)

        if self.current_state == grid_state:
            msg = GridConnectedInput(asset_container)

        self.run(msg)

class Blackout(State):
    def __init__(self):
        self.name = "Blackout State"

    def request(self, m):
        if not m.grid_alarm and m.grid_enabled:
            return grid_state
        else:
            return blackout_state

    def transition(self, m, requested_state):
        if requested_state == grid_state and m.grid_breaker_closed:
            return grid_state
        else:
            return blackout_state

    def action(self, m, requested_state):
        if requested_state == grid_state:
            m.grid_run = True

        else:
            m.grid_run = False

class BlackoutInput(StateMachineMessage):
    def __init__(self, asset_container):
        super(BlackoutInput, self).__init__(asset_container)

        grid = asset_container.get_asset('grid')[0]

        self.grid_breaker_closed = grid.status['online']
        self.grid_alarm = grid.status['alarm']
        self.grid_enabled = grid.status['enabled']

        self.grid_run = grid.control['run']

class GridConnected(State):
    def __init__(self):
        self.name = "Grid Connected State"

    def request(self, m):
        if not m.grid_enabled:
            return blackout_state
        else:
            return grid_state

    def transition(self, m, requested_state):
        if m.grid_alarm or not m.grid_breaker_closed:
            return blackout_state
        else:
            return grid_state

    def action(self, m, requested_state):
        if requested_state == blackout_state:
            m.grid_run = False


class GridConnectedInput(StateMachineMessage):
    def __init__(self, asset_container):
        super(GridConnectedInput, self).__init__(asset_container)

        grid = asset_container.get_asset('grid')[0]

        self.grid_breaker_closed = grid.status['online']
        self.grid_alarm = grid.status['alarm']
        self.grid_enabled = grid.status['enabled']

        self.grid_run = grid.control['run']

class InverterGridForming(State):
    def __init__(self):
        self.name = "Inverter Grid Forming State"

    def request(self, s_input):
        pass

    def transition(self, s_input, requested_state):
        pass

    def action(self, s_input, requested_state):
        pass

blackout_state = Blackout()
grid_state = GridConnected()
ess_state = InverterGridForming()

